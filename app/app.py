import logging
import os
import sys
import traceback
from _socket import timeout

import cherrypy
from flask import Flask
from flask import request
from paste.translogger import TransLogger


print(sys.path.append(os.getcwd()))

from utils import text_extractor
from apputils import text_prettifer
import main_flow
from algorithms import window_key_word_based_algo
from daos.brokenlinks import broken_link_manager

app = Flask(__name__)
print(os.path.dirname(os.path.realpath(__file__)))

with app.app_context():
    broken_link_dao = broken_link_manager.BrokenLinkClient(app)

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
        all_text, title = text_extractor.get_all_text_from_url(url=url)
        ingred_paragraph, instr_paragraph = window_key_word_based_algo.extract(ingredients, instructions, all_text)
        return create_json_response(ingred_paragraph, instr_paragraph, title, url)
    except BlockingIOError as exc:
        return jsonify({"error": f"The requests to {url} has been blocked temporarily "
                                 f"duo to repeated failed attempts."}), 500
    except ValueError as exc:
        traceback.print_exc()
        return jsonify({"error": f"Could not handle request to {url}."}), 500
    except timeout as exc:
        return jsonify({"error": f"The request to {url} has timed out."}), 500



def create_json_response(ingred_paragraph, instr_paragraph, title, url):
    json_response = text_prettifer.process({'ingredients': ingred_paragraph,
                                            'instructions': instr_paragraph})
    json_response['title'] = title
    json_response['url'] = url
    return json_response


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
