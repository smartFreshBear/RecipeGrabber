import atexit
import os
import shutil
import pytest
from flask import Flask

from daos.models.stored_recipes.test import recipes_mocks
from daos.database import DataBase
from services.broken_links_service import ServicesManager


@pytest.fixture(scope='package')
def recipes_dao():
	app = Flask(__name__)
	with app.app_context():
		db = DataBase(app)
		db_instance = db.get_db_instance()
		recipes_dao = ServicesManager(db_instance)
		db_instance.create_all()
		yield recipes_dao


def cleanup():
	current_dir = os.path.dirname(os.path.abspath(__file__))
	directory_to_delete = os.path.join(
			current_dir, '../instance'
			)

	shutil.rmtree(directory_to_delete)


def test_insert_logic(recipes_dao):
	for recipe in recipes_mocks.recipes_mocks:
		url = recipe['url']
		ingred = recipe['ingredients']
		instruct = recipe['instructions']
		if not recipes_dao.url_in_db(url):
			recipes_dao.add_recipe_to_db(response=recipe)
		stored_recipe = recipes_dao.get_recipe_from_db(
				url, ingred, instruct
				)
		assert recipe == stored_recipe


def test_retrieve_logic(recipes_dao):
	index = 0
	while index < len(recipes_mocks.repeated_urls):
		recipe = recipes_mocks.recipes_mocks[index]
		url = recipe['url']
		ingred = recipe['ingredients']
		instruct = recipe['instructions']
		if not recipes_dao.url_in_db(url):
			recipes_dao.add_recipe_to_db(response=recipe)
		stored_recipe = recipes_dao.get_recipe_from_db(
				recipes_mocks.repeated_urls[index], ingred, instruct
				)
		assert recipes_mocks.recipes_mocks[index] == stored_recipe
		index += 1


def test_delete_logic(recipes_dao):
	for recipe in recipes_mocks.recipes_mocks:
		url = recipe['url']
		if not recipes_dao.url_in_db(url):
			recipes_dao.add_recipe_to_db(response=recipe)
		recipes_dao.delete_recipe_from_db(url)
		assert not recipes_dao.url_in_db(url)


atexit.register(cleanup)
