import logging
import traceback
from _socket import timeout
from typing import List

import redis
from flask import jsonify
from werkzeug.exceptions import UnprocessableEntity

from algorithms.recipe_extarctor_algorithm import ExtractorAlgorithm
from apputils import text_prettifer
from apputils.constants import Constants
from common.exceptions.exceptions import WeCouldNotParseTheResponse
from services.stored_recipes_service import StoredRecipesService
from utils.text_extractor import TextExtractor


class TextExtractorService:
    def __init__(self, db, executor, caching_manager,
                 initial_algorithm: ExtractorAlgorithm,
                 llm_algorithm: ExtractorAlgorithm):
        self.executor = executor
        self.stored_recipes_service = StoredRecipesService(db)
        self.caching_manager = caching_manager
        self.text_extractor = TextExtractor(caching_manager)
        self.extractor_algorithm = initial_algorithm
        self.llm_algorithm = llm_algorithm

    def find_recipe_in_url(self, form):
        url = form['url']
        instructions = getattr(form, 'instructions', 'true').lower() == "true"
        ingredients = getattr(form, 'ingredients', 'true').lower() == "true"
        try:
            if self.stored_recipes_service.url_in_db(url):
                recipe = self.stored_recipes_service.get_recipe_from_db(url, ingredients, instructions)
                return jsonify(recipe)

            all_text, title = self.text_extractor.get_all_text_from_url(url=url)
            response = self.extract_recipe_given_text(all_text, title, url)
            self.executor.submit(self.stored_recipes_service.add_recipe_to_db, response=response)

            return response

        except UnprocessableEntity as exc:
            logging.error(f'UnprocessableEntity: {exc}')
            return jsonify({"error": f"Could not handle request to {url}."}), 422

        except BlockingIOError as exc:
            print(f'BlockingIOError: {exc}')
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

    @staticmethod
    def size_sanity_check(texts: List[str]) -> bool:

        amount_of_words = sum([len(text.split(' ')) for text in texts])

        if amount_of_words > Constants.MIN_RECIPE_SIZE:
            return True
        raise WeCouldNotParseTheResponse('too small response from web')

    def extract_recipe_given_text(self, all_text: str, title: str, url: str):

        self.size_sanity_check([all_text])

        ingred_paragraph, instr_paragraph = self.extractor_algorithm.extract(all_text)
        # TODO - need to extact to function that check list of words, sum it and then comaring, we call it - check sanitiy size
        self.size_sanity_check(ingred_paragraph + instr_paragraph)
        json_response = text_prettifer.process({"ingredients": ingred_paragraph,
                                                "instructions": instr_paragraph})

        try:
            ingred_paragraph, instr_paragraph = (
                self.llm_algorithm.extract(str(json_response)))

        except Exception as exc:
            logging.error(f"llm_algorithm failed becayse: {exc}, falling back to smaller model")


        self.size_sanity_check(ingred_paragraph + instr_paragraph)

        response = self.create_json_response(ingred_paragraph, instr_paragraph, title, url)
        return response


    def check_if_text_in_recipe(self, form):
        all_text = form['text']

        return self.extract_recipe_given_text(all_text, "<title>", "")

    @staticmethod
    def create_json_response(ingredients: str,
                             instruction: str,
                             title:str,
                             url: str):

        return {'ingredients': ingredients,
                         'instructions': instruction,
                         'title': title,
                         'url': url}
