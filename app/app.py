
import os
import sys

from flask import Flask
from flask import request


import django
from django.conf import settings
from django.template import Template, Context
TEMPLATES = [{'BACKEND':  'django.template.backends.django.DjangoTemplates'}]
settings.configure(TEMPLATES=TEMPLATES)
django.setup()

print(sys.path.append(os.getcwd()))
import parsers.parser

import main_flow
from utils import textExtractor
import gevent
from geventwebsocket.handler import WebSocketHandler

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


@app.route('/find_recipe_in_url/', methods=['POST'])
def find_recipe_in_url():
    url = request.form['url']
    instructions = request.form['instructions'].lower() == "true"
    ingredients = request.form['ingredients'].lower() == "true"

    array_of_paragraphs_from_website = textExtractor.get_text_from_url(url=url)

    answer = ''

    for paragraph in array_of_paragraphs_from_website:

        is_ingri = ingredients and main_flow.main_flow.predict_ingri(paragraph)
        is_instruc = instructions and main_flow.main_flow.predict_instru(paragraph)
        is_recipe = float(1)
        if is_ingri == is_recipe or is_instruc == is_recipe:
            answer += paragraph

    return answer


@app.route('/bottom_line_recipe_for/', methods=['GET'])
def bottom_line_recipe_for():
    url = request.args.get('url')
    ingredients, instructions = extract(True, True, url)

    c = Context({"ingredients": '\n'.join(ingredients),
                 "instructions": '\n '.join(instructions)})

    return template.render(c)

@app.route('/find_recipe_in_url_new/', methods=['POST'])
def find_recipe_in_url_window_algo_based():
    url = request.form['url']

    instructions = request.form['instructions'].lower() == "true"
    ingredients = request.form['ingredients'].lower() == "true"

    ingred_paragraph, instr_paragraph = extract(ingredients, instructions, url)

    return {'ingredients': ingred_paragraph,
            'instructions': instr_paragraph}


def extract(ingredients, instructions, url):
    ingred_paragraph = {}
    instr_paragraph = {}
    all_text = textExtractor.get_all_text_from_url(url=url)
    lines_of_text = list(filter(None, all_text.split('\n')))
    if ingredients:
        all_relevant_ingred_indies = parsers.parser.find_line_with_key_word(lines_of_text, True)
        max_num_of_lines_ingred = 0

        # find ingred paragraph with max number of lines
        for i in range(0, len(all_relevant_ingred_indies)):
            first_line = all_relevant_ingred_indies[i]
            last_line = parsers.parser.find_last_index_if_ingred(first_line, lines_of_text)
            new_size_of_text = last_line - first_line
            if new_size_of_text > max_num_of_lines_ingred:
                first_line_ingred = first_line
                last_line_ingred = last_line
                max_num_of_lines_ingred = new_size_of_text
                ingred_paragraph = parsers.parser.get_paragraph_from_indexes(first_line_ingred, last_line_ingred,
                                                                             lines_of_text)
    if instructions:
        # find instr paragraph with max number of lines
        all_relevant_instr_indies = parsers.parser.find_line_with_key_word(lines_of_text, False)
        max_num_of_lines_instr = 0

        for i in range(0, len(all_relevant_instr_indies)):
            first_line = all_relevant_instr_indies[i]
            last_line = parsers.parser.find_last_index_if_instruc(first_line, lines_of_text)
            new_size_of_text = last_line - first_line
            if new_size_of_text > max_num_of_lines_instr:
                first_line_instr = first_line
                last_line_instr = last_line
                max_num_of_lines_instr = new_size_of_text
                instr_paragraph = parsers.parser.get_paragraph_from_indexes(first_line_instr, last_line_instr,
                                                                            lines_of_text)
    return ingred_paragraph, instr_paragraph


if __name__ == '__main__':
    server = gevent.pywsgi.WSGIServer( (u'0.0.0.0', 5000), app, handler_class=WebSocketHandler )
    server.serve_forever()
    #app.run()
