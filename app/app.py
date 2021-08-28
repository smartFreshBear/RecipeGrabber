
import os
import sys

import django
from django.conf import settings
from django.template import Template, Context
from flask import Flask
from flask import request

TEMPLATES = [{'BACKEND':  'django.template.backends.django.DjangoTemplates'}]
settings.configure(TEMPLATES=TEMPLATES)
django.setup()

print(sys.path.append(os.getcwd()))

import main_flow
from algorithms import window_key_word_based_algo
import gevent
from geventwebsocket.handler import WebSocketHandler
import re
app = Flask(__name__)

print(os.path.dirname(os.path.realpath(__file__)))

application = app

main_flow.main_flow.main()

AMOUNT_OF_LINES = 7

print("server is up and running :)")

templateHtml = """
<!DOCTYPE html>
<html lang="en">
   <h1 style="color: #5e9ca0; text-align: right;">:המתכון</h1>
   <h2 style="color: #2e6c80; text-align: right;">:מצרכים</h2>
   <ol style="list-style-type: hebrew; direction: rtl;">
      <p style="text-align: right;">{{ingredients}}</p>
   </ol>
   <h2 style="color: #2e6c80; text-align: right;">:הוראות הכנה</h2>
   <p style="text-align: right;">{{instructions}}</p>
   <p><strong>&nbsp;</strong></p>
</html>
"""

template = Template(templateHtml)


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

    c = Context({"ingredients": '\n'.join(ingredients),
                 "instructions": '\n '.join(instructions)})

    return template.render(c)

@app.route('/find_recipe_in_url/', methods=['POST'])
def find_recipe_in_url_window_algo_based():
    url = request.form['url']

    instructions = request.form['instructions'].lower() == "true"
    ingredients = request.form['ingredients'].lower() == "true"

    ingred_paragraph, instr_paragraph = window_key_word_based_algo.extract(ingredients, instructions, url)

    return {'ingredients': ingred_paragraph,
            'instructions': instr_paragraph}


def remove_unwanted_patterns(text):
    url_regex = r'([\w]+(\/.*?\.[\w:]+))|([\w+]+\:\/\/)?([\w\d-]+\.)*[\w-]+[\.\:]\w+([\/\?\=\&\#.]?[-\w\+\,\%\=\'\"\:\/]+)*\/?'
    fixed_doc = []
    for row in text:
        fixed_doc.append(re.sub(url_regex, '', row))
    return fixed_doc


if __name__ == '__main__':
    server = gevent.pywsgi.WSGIServer( (u'0.0.0.0', 5000), app, handler_class=WebSocketHandler )
    server.serve_forever()
    #app.run()
