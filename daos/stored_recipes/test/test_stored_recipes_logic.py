import pytest

from flask import Flask
import recipes_mocks
from daos.database import DataBase
from daos.stored_recipes import stored_recipes_manager

app = Flask(__name__)
app.config['URL_TIMEOUT'] = 10
app.app_context().push()
with app.app_context():
	db = DataBase(app)
	db_instance = db.get_db_instance()
	db_instance.drop_all()
	stored_recipe_dao = stored_recipes_manager.RecipeService(
			db_instance
			)
	db_instance.create_all()


def test_insert_logic(self):
	for recipe in recipes_mocks.recipes_mocks:
		url = recipe['url']
		ingred = recipe['ingredients']
		instruct = recipe['instructions']
		if not stored_recipe_dao.url_in_db(url):
			stored_recipe_dao.add_recipe_to_db(response=recipe)
		stored_recipe = stored_recipe_dao.get_recipe_from_db(
				url, ingred, instruct
				)
		assert recipe == stored_recipe


def test_retrieve_logic(self):
	index = 0
	while index < len(recipes_mocks.repeated_urls):
		recipe = recipes_mocks.recipes_mocks[index]
		url = recipe['url']
		ingred = recipe['ingredients']
		instruct = recipe['instructions']
		if not stored_recipe_dao.url_in_db(url):
			stored_recipe_dao.add_recipe_to_db(response=recipe)
		stored_recipe = stored_recipe_dao.get_recipe_from_db(
				recipes_mocks.repeated_urls[index], ingred, instruct
				)
		assert recipes_mocks.recipes_mocks[index] == stored_recipe
		index += 1


def test_delete_logic(self):
	for recipe in recipes_mocks.recipes_mocks:
		url = recipe['url']
		if not stored_recipe_dao.url_in_db(url):
			stored_recipe_dao.add_recipe_to_db(response=recipe)
		stored_recipe_dao.delete_recipe_from_db(url)
		assert not stored_recipe_dao.url_in_db(url)
