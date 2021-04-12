from flask import Flask
from flask import request

import main_flow
from utils import textExtractor
import parser.parser


app = Flask(__name__)

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

@app.route('/find_recipe_in_url_new/', methods=['POST'])
def find_recipe_in_url_window_algo_based():
    url = request.form['url']
    instructions = request.form['instructions'].lower() == "true"
    ingredients = request.form['ingredients'].lower() == "true"


    all_text = textExtractor.get_all_text_from_url(url=url)

    all_relevant_ingrid_indies = parser.parser.find_line_with_key_word_ingrid(all_text)

    lines_of_text = all_text.split('\n')

    for i in all_relevant_ingrid_indies:
        parser.parser.is_window_valid("\n".join(lines_of_text[i : i + AMOUNT_OF_LINES]))

    answer = ''

    # for paragraph in array_of_paragraphs_from_website:
    #
    #     is_ingri = ingredients and main_flow.main_flow.predict_ingri(paragraph)
    #     is_instruc = instructions and main_flow.main_flow.predict_instru(paragraph)
    #     is_recipe = float(1)
    #     if is_ingri == is_recipe or is_instruc == is_recipe:
    #         answer += paragraph

    return answer


if __name__ == '__main__':

    app.run()


def main():
    app.run()
