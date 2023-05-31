import logging
import traceback
from _socket import timeout

from flask import jsonify

from algorithms import window_key_word_based_algo
from apputils import text_prettifer
from services.stored_recipes_service import StoredRecipesService
from utils import text_extractor


class TextExtractorService:
    def __init__(self, db, executor):
        self.executor = executor
        self.stored_recipes_service = StoredRecipesService(db)

    def find_recipe_in_url(self, form):
        url = form['url']
        instructions = form['instructions'].lower() == "true"
        ingredients = form['ingredients'].lower() == "true"
        try:
            if self.stored_recipes_service.url_in_db(url):
                return jsonify(self.stored_recipes_service.get_recipe_from_db(url, ingredients, instructions))
            all_text, title = text_extractor.get_all_text_from_url(url=url)
            ingred_paragraph, instr_paragraph = window_key_word_based_algo.extract(ingredients, instructions, all_text)
            response = self.create_json_response(ingred_paragraph, instr_paragraph, title, url)
            self.executor.submit(self.stored_recipes_service.add_recipe_to_db, response=response)
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

    def check_if_text_in_recipe(self, form):
        all_text = form['text']

        ingredients, instructions = window_key_word_based_algo.extract(True, True, all_text)
        return self.create_json_response(ingredients, instructions, '', '')

    @staticmethod
    def create_json_response(ingred_paragraph, instr_paragraph, title, url):
        json_response = text_prettifer.process({'ingredients': ingred_paragraph,
                                                'instructions': instr_paragraph})
        json_response['title'] = title
        json_response['url'] = url
        return json_response
