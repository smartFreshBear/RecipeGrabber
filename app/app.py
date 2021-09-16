
import os
import sys

from flask import Flask
from flask import request


from algorithms import window_key_word_based_algo
from exreamlystupidui import html_renderer
from apputils import text_prettifer
import gevent
from geventwebsocket.handler import WebSocketHandler

from utils import textExtractor

print(sys.path.append(os.getcwd()))
import main_flow

app = Flask(__name__)
print(os.path.dirname(os.path.realpath(__file__)))


application = app

main_flow.main_flow.main()

print("server is up and running :)")

@app.route('/isServerUp')
def is_server_up():
    return "Yes, Server is up"


@app.route('/train')
def train():
    return main_flow.main_flow.main()


@app.route('/find_recipe_in_text/', methods=['POST'])
def check_if_text_is_recipe():
    all_text = request.form['text']

    ingredients, instructions = window_key_word_based_algo.extract(True, True, all_text)
    return create_json_response(ingredients, instructions)


@app.route('/ma_tachles/', methods=['GET'])
def bottom_line_recipe_for():
    url = request.args.get('url')
    all_text = textExtractor.get_all_text_from_url(url=url)

    ingredients, instructions = window_key_word_based_algo.extract(True, True, all_text)

    return html_renderer.render_given_json(create_json_response(ingredients, instructions))


@app.route('/', methods=['GET'])
def home_page():
    return html_renderer.render_home_page()


@app.route('/find_recipe_in_url/', methods=['POST'])
def find_recipe_in_url_window_algo_based():
    url = request.form['url']

    instructions = request.form['instructions'].lower() == "true"
    ingredients = request.form['ingredients'].lower() == "true"

    all_text = textExtractor.get_all_text_from_url(url=url)
    ingred_paragraph, instr_paragraph = window_key_word_based_algo.extract(ingredients, instructions, all_text)

    return create_json_response(ingred_paragraph, instr_paragraph)


def create_json_response(ingred_paragraph, instr_paragraph):
    return text_prettifer.process({'ingredients': ingred_paragraph,
                                   'instructions': instr_paragraph})


if __name__ == '__main__':
    server = gevent.pywsgi.WSGIServer( (u'0.0.0.0', 5000), app, handler_class=WebSocketHandler )
    server.serve_forever()