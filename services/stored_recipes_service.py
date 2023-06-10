import logging
from sqlite3 import IntegrityError

from daos.models.stored_recipes.stored_recipes_model import define_stored_recipe


class StoredRecipesService:
    def __init__(self, db):
        self.db = db
        self.StoredRecipe = define_stored_recipe(self.db)

    def add_recipe_to_db(self, **kwargs):
        response = kwargs.get("response")
        if response is None:
            return
        try:
            if self.url_in_db(response['url']):
                return

            requested_url = self.StoredRecipe(
                url=response.get("url").strip(),
                title=response.get("title"),
                ingredients=response.get("ingredients"),
                instructions=response.get("instructions")
            )
            self.db.session.add(requested_url)
            self.db.session.commit()
            requested_recipe = self.db.session.query(self.StoredRecipe). \
                filter_by(url=response.get("url").strip()).first()
            logging.info(
                "new recipe stored:\n{}".format(requested_recipe)
            )
        except IntegrityError:
            logging.error(
                "{} url key already inserted".format(response.get("url"))
            )
        except (TypeError, AttributeError):
            logging.error(
                "The following input parameter was invalid:\n{}"
                .format(response)
            )

    def url_in_db(self, url):
        requested_url = self.db.session.query(self.StoredRecipe).filter_by(
            url=url.strip()
        ).first()
        return requested_url is not None

    def get_recipe_from_db(self, url, ingredients=True, instructions=True):
        if not self.url_in_db(url):
            logging.error(
                "URL does not exists in database."
            )
            raise ValueError

        requested_url = self.db.session.query(self.StoredRecipe). \
            filter_by(url=url.strip()).first()

        json_response = {
            "url": url,
            "title": requested_url.title,
            "ingredients": [],
            "instructions": []
        }
        if ingredients:
            json_response["ingredients"] = requested_url.ingredients

        if instructions:
            json_response["instructions"] = requested_url.instructions

        return json_response

    def delete_recipe_from_db(self, url, ):
        if not self.url_in_db(url):
            logging.info("Could not delete. URL is not in the database.")
            return
        requested_url = self.db.session.query(self.StoredRecipe). \
            filter_by(url=url.strip()).first()
        self.db.session.delete(requested_url)
        self.db.session.commit()
