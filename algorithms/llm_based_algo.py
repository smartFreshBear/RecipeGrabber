"""
This will call small microservice that will use langchain to summerize the recipe
it will send a "clean" version of the website.
"""
import os

import requests

from algorithms.recipe_extarctor_algorithm import ExtractorAlgorithm

LLM_BASED_ALGO_HOST_AND_PORT = os.environ.get('LLM_BASED_ALGO_HOST_AND_PORT', 'localhost:8844')


class LlmBasedAlgo(ExtractorAlgorithm):

    def extract(self, text) -> (str, str):
        """
        send a get request to the microservice with the llm
        using the requests library
        """
        response = requests.get(f"http://{LLM_BASED_ALGO_HOST_AND_PORT}/summarize_recipe",
                                json={"text": text},
                                headers={'Cache-Control': 'no-cache'})
        return response.json()["ingredients"], response.json()["instructions"]
