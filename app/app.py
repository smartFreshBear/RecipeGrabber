
import os

# import django
# from django.conf import settings
from flask import Flask
from flask import request

# TEMPLATES = [{'BACKEND':  'django.template.backends.django.DjangoTemplates'}]
# settings.configure(TEMPLATES=TEMPLATES)
# django.setup()

import main_flow
from algorithms import window_key_word_based_algo
from exreamlystupidui import html_renderer
from apputils import text_prettifer
import gevent
from geventwebsocket.handler import WebSocketHandler

app = Flask(__name__)

print(os.path.dirname(os.path.realpath(__file__)))

application = app

main_flow.main_flow.main()

AMOUNT_OF_LINES = 7

print("server is up and running :)")

@app.route('/isServerUp')
def is_server_up():
    return "Yes, Server is up"


@app.route('/train')
def train():
    return main_flow.main_flow.main()


@app.route('/is_text_recipe/', methods=['POST'])
def check_if_text_is_recipe():
    text = request.form['text']
    is_ingri = main_flow.main_flow.predict_ingri(text)
    is_instruc = main_flow.main_flow.predict_instru(text)
    ans = 'we predicated its is {} for ingratiates and {} for instruction'.format(is_ingri, is_instruc)
    return ans


@app.route('/ma_tachles/', methods=['GET'])
def bottom_line_recipe_for():
    url = request.args.get('url')
    ingredients, instructions = window_key_word_based_algo.extract(True, True, url)

    return html_renderer.render_given_json(create_json_response(ingredients, instructions))

@app.route('/', methods=['GET'])
def home_page():
    return html_renderer.render_home_page()


@app.route('/find_recipe_in_url/', methods=['POST'])
def find_recipe_in_url_window_algo_based():
    url = request.form['url']

    instructions = request.form['instructions'].lower() == "true"
    ingredients = request.form['ingredients'].lower() == "true"

    ingred_paragraph, instr_paragraph = window_key_word_based_algo.extract(ingredients, instructions, url)



    return create_json_response(
        text_prettifer.process(ingred_paragraph),
        text_prettifer.process(instr_paragraph))


def create_json_response(ingred_paragraph, instr_paragraph):
    return {'ingredients': text_prettifer.process(ingred_paragraph),
            'instructions': text_prettifer.process(instr_paragraph)}


if __name__ == '__main__':
    server = gevent.pywsgi.WSGIServer( (u'0.0.0.0', 5000), app, handler_class=WebSocketHandler )
    server.serve_forever()
    #app.run()
