import logging
import traceback
from _socket import timeout
import redis
from flask import jsonify, json

from algorithms import window_key_word_based_algo
from apputils import text_prettifer
from services.stored_recipes_service import StoredRecipesService
from utils import text_extractor


class TextExtractorService:
    def __init__(self, crud, executor, caching_manager):
        self.executor = executor
        self.stored_recipes_service = StoredRecipesService(crud)
        self.caching_manager = caching_manager

    def find_recipe_in_url(self, form):
        url = form['url']
        instructions = form['instructions'].lower() == "true"
        ingredients = form['ingredients'].lower() == "true"
        try:
            if self.caching_manager.exists_in_cache(key=url, name="frequently_used_recipes"):
                return jsonify(json.loads(self.caching_manager.get_from_cache(name="frequently_used_recipes", key=url)))
            if recipe := self.stored_recipes_service.get_recipe_from_db(url, ingredients, instructions):
                self.caching_manager.cache_url(key=url, value=json.dumps(recipe), name="frequently_used_recipes")
                return jsonify(recipe)

            all_text, title = text_extractor.get_all_text_from_url(url=url, caching_manager=self.caching_manager)
            ingred_paragraph, instr_paragraph = window_key_word_based_algo.extract(ingredients, instructions, all_text)
            response = self.create_json_response(ingred_paragraph, instr_paragraph, title, url)

            self.caching_manager.cache_url(key=url, value=json.dumps(response), name="frequently_used_recipes")
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
        except redis.RedisError as exc:
            logging.error(exc)
            return jsonify({"error": "Redis Caching error"}), 500
        except Exception:
            logging.exception("Unexpected error")
            return jsonify({"error": "Unexpected error"}), 500

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
