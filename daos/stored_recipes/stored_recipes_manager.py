import logging
from dataclasses import dataclass
from sqlite3 import IntegrityError


def define_class(db):
    @dataclass
    class StoredRecipe(db.Model):
        __table_args__ = { 'extend_existing': True }
        id: int = db.Column(db.Integer, primary_key=True)
        url: str = db.Column(db.String(250), unique=True, nullable=False)
        title: str = db.Column(db.String(250), nullable=False)
        ingredients: list = db.Column(
                db.PickleType(), nullable=False, default=[]
                )
        instructions: list = db.Column(
                db.PickleType(), nullable=False, default=[]
                )

    return StoredRecipe


class RecipeService:
    def __init__(self, db):
        self.db = db
        self.StoredRecipe = define_class(self.db)
        self.requested_url = None

    def add_recipe_to_db(self, **kwargs):
        response = kwargs.get("response")
        if response is None:
            return
        try:
            if self.url_in_db(response['url']):
                return

            self.requested_url = self.StoredRecipe(
                    url=response.get("url").strip(),
                    title=response.get("title"),
                    ingredients=response.get("ingredients"),
                    instructions=response.get("instructions")
                    )
            self.db.session.add(self.requested_url)
            self.db.session.commit()
            self.requested_url = self.db.session.query(self.StoredRecipe). \
                filter_by(url=response.get("url").strip()).first()
            logging.info(
                    "new recipe stored:\n{}".format(self.requested_url)
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
        self.requested_url = self.db.session.query(self.StoredRecipe).filter_by(
                url=url.strip()
                ).first()
        return self.requested_url is not None

    def get_recipe_from_db(self, url, ingredients=True, instructions=True):
        if not self.requested_url.url or self.requested_url.url != url.strip():
            self.requested_url = self.db.session.query(self.StoredRecipe). \
                filter_by(url=url.strip()).first()
        json_response = {
                "url":          url,
                "title":        self.requested_url.title,
                "ingredients":  [],
                "instructions": []
                }
        if ingredients:
            json_response["ingredients"] = self.requested_url.ingredients

        if instructions:
            json_response["instructions"] = self.requested_url.instructions

        return json_response

    def delete_recipe_from_db(self, url,):
        if not self.url_in_db(url):
            logging.info("Could not delete. URL is not in the database.")
            return
        self.db.session.delete(self.requested_url)
        self.db.session.commit()

