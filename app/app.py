import logging
import os
import sys

from flask_executor import Executor
import cherrypy
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from paste.translogger import TransLogger

from daos.caching_manager import CachingManager
from routes.routes import api_bp, Routes
import main_flow

print(sys.path.append(os.getcwd()))


app = Flask(__name__)
app.config['URL_TIMEOUT'] = 10
app.config['EXECUTOR_TYPE'] = 'thread'
app.config['EXECUTOR_MAX_WORKERS'] = 2
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///recipeGrabber.sqlite"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

app.app_context().push()
print(os.path.dirname(os.path.realpath(__file__)))
db = SQLAlchemy(app)
executor = Executor(app)
caching_manager = CachingManager()


with app.app_context():
    routes = Routes(db, executor, caching_manager)
    app.register_blueprint(api_bp)
    db.create_all()


main_flow.main_flow.main()

STATIC_URL = "/static/"

logging.info("server is up and running :)")





def run_server():
    # Enable WSGI access logging via Paste
    app_logged = TransLogger(app)

    # Mount the WSGI callable object (app) on the root directory
    cherrypy.tree.graft(app_logged, '/')

    # Set the configuration of the web server
    cherrypy.config.update({
        'engine.autoreload_on': True,
        'log.screen': True,
        'server.socket_port': 5000,
        'server.socket_host': '0.0.0.0'
    })

    # Start the CherryPy WSGI web server
    cherrypy.engine.start()
    cherrypy.engine.block()


if __name__ == '__main__':
    # server = gevent.pywsgi.WSGIServer((u'0.0.0.0', 5000), app, handler_class=WebSocketHandler)
    # server.serve_forever()
    run_server()


