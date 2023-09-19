import os
import sys

from flask_executor import Executor
import cherrypy
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from paste.translogger import TransLogger

from packages.recipesql import CrudSQL
from daos.caching_manager import CachingManager
from routes.routes import api_bp, Routes
import main_flow
from utils.logger import create_logger_instance

print(sys.path.append(os.getcwd()))

app = Flask(__name__)
app.config.from_pyfile("config.py")


app.app_context().push()
print(os.path.dirname(os.path.realpath(__file__)))
db = SQLAlchemy(app)
executor = Executor(app)
caching_manager = CachingManager()


with app.app_context():
    crud = CrudSQL(db)
    routes = Routes(crud, executor, caching_manager)
    app.register_blueprint(api_bp)



main_flow.main_flow.main()

STATIC_URL = "/static/"

app_logger = create_logger_instance('App')
app_logger.info("server is up and running :)")


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


