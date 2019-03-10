from flask import Flask, session
from flask_session import Session
from cloudalbum import application as CloudAlbum
from cloudalbum.config import conf
from cloudalbum import util
from redis import StrictRedis
import os, socket

app = Flask(__name__)

# Flask Session for Redis
#app.config['SESSION_TYPE'] = 'redis'
#app.config['SESSION_REDIS'] = StrictRedis(host='<ELASTICACHE_ENDPOINT>', port=<PORT>)
#Session(app)


# This code is inserted for only LAB02.
@app.template_filter()
def get_ip_addr(value):
    hostname = '({0})'.format(socket.gethostname())
    return hostname


if __name__ == '__main__':
    util.check_variables()

    app = CloudAlbum.init_app(app)
    app.logger.debug('DB_URL: {0}'.format(conf['DB_URL']))
    app.logger.debug('GMAPS_KEY: {0}'.format(conf['GMAPS_KEY']))

    app.run(host=conf['APP_HOST'], port=conf['APP_PORT'], debug=True)


