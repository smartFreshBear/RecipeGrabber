

from daos.models.stored_recipes.stored_recipes_model import define_stored_recipe
from packages.recipesql.utils.errors import UniqueError


class StoredRecipesService:
    def __init__(self, crud):
        self.crud = crud
        self.StoredRecipe = define_stored_recipe(crud.db)

    def add_recipe_to_db(self, **kwargs: dict):
        try:
            response = kwargs.get("response", {"empty": None})
            if "empty" in response:
                raise ValueError

            return self.crud.save_one(self.StoredRecipe(
                url=response.get("url","N/A").strip(),
                title=response.get("title",""),
                ingredients=response.get("ingredients",[]),
                instructions=response.get("instructions",[])
            ))
        except UniqueError:
            return
        except Exception as exc:
            return exc

    def get_recipe_from_db(self, url, ingredients=True, instructions=True):
        try:
            requested_url = self.crud.find_one(self.StoredRecipe(
                                                    url=url.strip(),
                                                    title="")
                                                )

            json_response = {
                "url": url.strip(),
                "title": requested_url.title,
                "ingredients": [],
                "instructions": []
            }
            if ingredients:
                json_response["ingredients"] = requested_url.ingredients

            if instructions:
                json_response["instructions"] = requested_url.instructions

            return json_response
        except UniqueError:
            return
        except Exception as exc:
            raise exc

    def delete_recipe_from_db(self, url):
        try:
            self.crud.delete_one(self.StoredRecipe(
                                            url=url.strip(),
                                            title="")
                                        )
        except Exception as exc:
            raise exc
