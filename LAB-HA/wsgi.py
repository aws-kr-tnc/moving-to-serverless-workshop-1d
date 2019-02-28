"""
    cloudalbum.application.py
    ~~~~~~~~~~~~~~~~~~~~~~~
    CloudAlbum is a sample application for TechSummit 2018 workshop.

    :copyright: © 2018 by Sungshik Jou.
    :license: BSD, see LICENSE for more details.
"""

from cloudalbum import login
from cloudalbum import util
from cloudalbum.config import conf
from cloudalbum.model import models
from cloudalbum.controlloer.errors import errorHandler
from cloudalbum.controlloer.user import userView
from cloudalbum.controlloer.site import siteView
from cloudalbum.controlloer.photo import photoView

from flask import redirect, url_for, current_app, request, Flask
from flask_session import Session
from flask_wtf.csrf import CSRFProtect

from logging.handlers import RotatingFileHandler
from logging import Formatter
from redis import StrictRedis

import os
import logging

application = Flask(__name__)

# Flask Session for Redis
application.config['SESSION_TYPE'] = 'redis'
application.config['SESSION_REDIS'] = StrictRedis(host=conf['ELCACHE_EP'], port=6379)
Session(application)

# Regist error handler
application.register_error_handler(404, errorHandler.not_found)
application.register_error_handler(405, errorHandler.server_error)
application.register_error_handler(500, errorHandler.server_error)
application.register_error_handler(400, errorHandler.csrf_error)

def get_log_level():
    """
    Determine logging level option from config file
    :return: logging level
    """
    level = conf['LOGGING_LEVEL']
    if level.lower() is 'info':
        return logging.INFO
    elif level.lower() is 'debug':
        return logging.DEBUG
    elif level.lower() is 'error':
        return logging.ERROR

    elif level.lower() is 'warn':
        return logging.WARN
    else :
        return logging.DEBUG


def url_for_other_page(page):
    """
    Function dor the page navigation.
    :param page: page number.
    :return: target page items.
    """
    args = request.view_args.copy()
    args['page'] = page
    return url_for(request.endpoint, **args)


@login.unauthorized_handler
def unauthorized_handler():
    """
    If unauthorized requests are arrived then redirect sign-in URL.
    :return: Redirect sign-in in page
    """
    current_app.logger.info("Unauthorized user need to sign-in")
    return redirect(url_for('userView.signin'))


util.check_variables()

csrf = CSRFProtect()
csrf.init_app(application)

# CSRF setup for Flask Blueprint module
userView.blueprint.before_request(csrf.protect)
siteView.blueprint.before_request(csrf.protect)

# Regist Flask Blueprint module
application.register_blueprint(siteView.blueprint, url_prefix='/')
application.register_blueprint(userView.blueprint, url_prefix='/users')
application.register_blueprint(photoView.blueprint, url_prefix='/photos')

# Setup application configuration
application.secret_key = conf['FLASK_SECRET']
application.config['SQLALCHEMY_DATABASE_URI'] = conf['DB_URL']
application.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = conf['SQLALCHEMY_TRACK_MODIFICATIONS']
application.config['SQLALCHEMY_ECHO'] = conf['DB_ECHO_FLAG']

# SQLITE doesn't support DB connection pool
if 'sqlite' not in conf['DB_URL'].lower():
    application.config['SQLALCHEMY_POOL_SIZE'] = conf['DB_POOL_SIZE']
    application.config['SQLALCHEMY_MAX_OVERFLOW'] = conf['DB_MAX_OVERFLOW']
    application.config['SQLALCHEMY_POOL_TIMEOUT'] = conf['DB_SQLALCHEMY_POOL_TIMEOUT']
    application.config['SQLALCHEMY_POOL_RECYCLE'] = conf['DB_SQLALCHEMY_POOL_RECYCLE']

application.jinja_env.globals['url_for_other_page'] = url_for_other_page

# Logger setup
application.config['LOGGING_LEVEL'] = get_log_level()
application.config['LOGGING_FORMAT'] = conf['LOGGING_FORMAT']
application.config['LOGGING_LOCATION'] = conf['LOG_FILE_PATH']
application.config['LOGGING_FILENAME'] = os.path.join(conf['LOG_FILE_PATH'], conf['LOG_FILE_NAME'])
application.config['LOGGING_MAX_BYTES'] = conf['LOGGING_MAX_BYTES']
application.config['LOGGING_BACKUP_COUNT'] = conf['LOGGING_BACKUP_COUNT']

util.log_path_check(conf['LOG_FILE_PATH'])
file_handler = RotatingFileHandler(application.config['LOGGING_FILENAME'],
                                   maxBytes=application.config['LOGGING_MAX_BYTES'],
                                   backupCount=application.config['LOGGING_BACKUP_COUNT'])
file_handler.setFormatter(Formatter(application.config['LOGGING_FORMAT']))
file_handler.setLevel(application.config['LOGGING_LEVEL'])

application.logger.addHandler(file_handler)
application.logger.setLevel(application.config['LOGGING_LEVEL'])
application.logger.info("logging start")

# Setup LoginManager
login.init_app(application)
login.login_view = 'userView.signin'

# Setup models for DB operations
with application.app_context():
    models.db.init_app(application)
    try:
        models.db.create_all()
    except Exception as e:
        application.logger.error(e)
        exit(-1)

application.logger.debug('DB_URL: {0}'.format(conf['DB_URL']))
application.logger.debug('GMAPS_KEY: {0}'.format(conf['GMAPS_KEY']))

if __name__ == '__main__':
    application.run()
