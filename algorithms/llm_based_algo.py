"""
This will call small microservice that will use langchain to summerize the recipe
it will send a "clean" version of the website.
"""
import requests

from algorithms.recipe_extarctor_algorithm import ExtractorAlgorithm


class LlmBasedAlgo(ExtractorAlgorithm):

    def extract(self, text) -> (str, str):
        """
        send a get request to the microservice with the llm
        using the requests library
        """
        response = requests.get("http://localhost:8001/summarize_recipe", json={"text": text},
                                headers={'Cache-Control': 'no-cache'})
        return response.json()["ingredients"], response.json()["instructions"]
