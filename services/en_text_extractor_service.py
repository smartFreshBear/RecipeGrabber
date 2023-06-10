from flask import jsonify


class EnglishTextExtractorService:
    def __init__(self):
        pass

    @staticmethod
    def find_recipe_in_url(form):
        url = form['url']
        instructions = form['instructions'].lower() == "true"
        ingredients = form['ingredients'].lower() == "true"

        return jsonify({
            "ingredients": ["Lorem ipsum dolor sit amet, consectetur adipiscing elit.",
                            "Integer eu posuere massa. Mauris ut lectus feugiat,",
                            "Lorem ipsum dolor sit amet, consectetur adipiscing elit.",
                            "Integer eu posuere massa. Mauris ut lectus feugiat."],
            "instructions": ["Lorem ipsum dolor sit amet, consectetur adipiscing elit.",
                             "Integer eu posuere massa. Mauris ut lectus feugiat,",
                             " mattis est vel, finibus ligula. Maecenas euismod lacus non pellentesque tempus."],
            "title": "Best Mock Recipe In The West",
            "url": "www.mock-example.com"
        }), 200
