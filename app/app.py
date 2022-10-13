import logging
import os
import sys

import gevent
from flask import Flask, jsonify
from flask import request
from geventwebsocket.handler import WebSocketHandler

print(sys.path.append(os.getcwd()))

from utils import textExtractor
from apputils import text_prettifer
import main_flow
from algorithms import window_key_word_based_algo
from daos.brokenlinks import broken_link_manager

app = Flask(__name__)
print(os.path.dirname(os.path.realpath(__file__)))

application = app

broken_link_dao = broken_link_manager.BrokenLinkClient(application)

main_flow.main_flow.main()

STATIC_URL = "/static/"

logging.info("server is up and running :)")


@app.route('/train')
def train():
    return main_flow.main_flow.main()


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

    all_text, title = textExtractor.get_all_text_from_url(url=url)
    ingred_paragraph, instr_paragraph = window_key_word_based_algo.extract(ingredients, instructions, all_text)

    return create_json_response(ingred_paragraph, instr_paragraph, title, url)


def create_json_response(ingred_paragraph, instr_paragraph, title, url):
    json_response = text_prettifer.process({'ingredients': ingred_paragraph,
                                            'instructions': instr_paragraph})
    json_response['title'] = title
    json_response['url'] = url
    return json_response


if __name__ == '__main__':
    server = gevent.pywsgi.WSGIServer((u'0.0.0.0', 5000), app, handler_class=WebSocketHandler)
    server.serve_forever()
