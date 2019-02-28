from waitress import serve

from flask import Flask, session
from flask_session import Session
from cloudalbum import application as CloudAlbum
from cloudalbum.config import conf
from cloudalbum import util
from redis import StrictRedis


app = Flask(__name__)

if __name__ == '__main__':
    util.check_variables()

    # Flask Session for Redis
    app.config['SESSION_TYPE'] = 'redis'
    app.config['SESSION_REDIS'] = StrictRedis(host=conf['ELCACHE_EP'], port=6379)
    Session(app)

    app = CloudAlbum.init_app(app)
    app.logger.debug('DB_URL: {0}'.format(conf['DB_URL']))
    app.logger.debug('GMAPS_KEY: {0}'.format(conf['GMAPS_KEY']))

    # application.run(host=conf['APP_HOST'], port=conf['APP_PORT'], debug=True)

    serve(app, host='0.0.0.0', port=8000)


