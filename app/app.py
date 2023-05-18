import logging
import os
import sys
import traceback
from _socket import timeout

from flask_executor import Executor
import cherrypy
from flask import Flask
from flask import request, jsonify
from paste.translogger import TransLogger

print(sys.path.append(os.getcwd()))

from utils import text_extractor
from apputils import text_prettifer
import main_flow
from algorithms import window_key_word_based_algo

from daos.database import DataBase
from daos.brokenlinks import broken_link_manager
from daos.stored_recipes import stored_recipes_manager

app = Flask(__name__)
app.config['URL_TIMEOUT'] = 10
app.config['EXECUTOR_TYPE'] = 'thread'
app.config['EXECUTOR_MAX_WORKERS'] = 2

app.app_context().push()
print(os.path.dirname(os.path.realpath(__file__)))
executor = Executor(app)

with app.app_context():
    db = DataBase(app)
    db_instance = db.get_db_instance()
    broken_link_dao = broken_link_manager.BrokenLinkClient(db_instance)
    stored_recipes_dao = stored_recipes_manager.RecipeService(db_instance)

    db_instance.create_all()

main_flow.main_flow.main()

STATIC_URL = "/static/"

logging.info("server is up and running :)")


@app.route('/train')
def train():
    try:
        return main_flow.main_flow.main()
    except RuntimeError as exc:
        traceback.print_exc()
        print(exc)


@app.route('/find_recipe_in_text/', methods=['POST'])
def check_if_text_is_recipe():
    all_text = request.form['text']

    ingredients, instructions = window_key_word_based_algo.extract(True, True, all_text)
    return create_json_response(ingredients, instructions, '', '')


@app.route('/add_url_to_investigation_list/', methods=['POST'])
def add_url_to_investigation_list():
    url = request.form['url']
    broken_link_dao.presist_broken_link(url, False)
    return {'status': 'OK'}


@app.route('/get_all_broken_links', methods=['GET'])
def get_all_broken_links():
    broken_links = broken_link_dao.get_all_broken_links()
    return broken_links


@app.route('/remove_broken_links_by_ids/', methods=['POST'])
def remove_broken_links_by_ids():
    ids_strs = request.form['ids']
    ids = list(map(lambda id_str: int(id_str), ids_strs.split(',')))
    what_is_it = broken_link_dao.delete_broken_links_by_ids(ids)
    return what_is_it


@app.route('/find_recipe_in_url/', methods=['POST'])
def find_recipe_in_url_window_algo_based():
    url = request.form['url']
    instructions = request.form['instructions'].lower() == "true"
    ingredients = request.form['ingredients'].lower() == "true"
    try:
        if stored_recipes_dao.url_in_db(url):
            return jsonify(stored_recipes_dao.get_recipe_from_db(url, ingredients, instructions))
        all_text, title = text_extractor.get_all_text_from_url(url=url)
        ingred_paragraph, instr_paragraph = window_key_word_based_algo.extract(ingredients, instructions, all_text)
        response = create_json_response(ingred_paragraph, instr_paragraph, title, url)
        executor.submit(stored_recipes_dao.add_recipe_to_db, response=response)
        return response
    except BlockingIOError as exc:
        return jsonify({"error": f"The requests to {url} has been blocked temporarily "
                                 f"duo to repeated failed attempts."}), 500
    except ValueError as exc:
        traceback.print_exc()
        return jsonify({"error": f"Could not handle request to {url}."}), 500
    except timeout as exc:
        return jsonify({"error": f"The request to {url} has timed out."}), 500
    except TimeoutError as exc:
        logging.error(traceback.print_exc())
        return jsonify({"error": "Threading error"}), 500


@app.route('/populate_training_example_from_url/', methods=['POST'])
def populate_training_example_from_url():
    password = request.form.get('password')

    if password != "toy_password":
        return {'error': 'Invalid password'}, 401

    return 'OK', 200

def create_json_response(ingred_paragraph, instr_paragraph, title, url):
    json_response = text_prettifer.process({'ingredients': ingred_paragraph,
                                            'instructions': instr_paragraph})
    json_response['title'] = title
    json_response['url'] = url
    return json_response


@app.route('/en/find_recipe_in_url/', methods=['POST'])
def en_find_recipe_in_url_window_algo_based():
    url = request.form['url']
    instructions = request.form['instructions'].lower() == "true"
    ingredients = request.form['ingredients'].lower() == "true"

    return jsonify({
        "ingredients": ["Lorem ipsum dolor sit amet, consectetur adipiscing elit.",
                            "Integer eu posuere massa. Mauris ut lectus feugiat,",
                        "Lorem ipsum dolor sit amet, consectetur adipiscing elit.",
                        "Integer eu posuere massa. Mauris ut lectus feugiat."],
        "instructions": ["Lorem ipsum dolor sit amet, consectetur adipiscing elit.",
                            "Integer eu posuere massa. Mauris ut lectus feugiat,",
                            " mattis est vel, finibus ligula. Maecenas euismod lacus non pellentesque tempus."],
        "title": "Best Mock Recipe In The West",
        "url": "www.mock-example.com"
    }), 200


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


