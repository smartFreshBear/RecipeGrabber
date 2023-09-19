from shutil import rmtree
import pytest

from flask_sqlalchemy import SQLAlchemy
from flask import Flask

from daos.models.users.user_model import define_user
from . import UsersMocks
from .. import CrudSQL
from ..utils.errors import ColumnError, TableError, UniqueError


# Run the test by calling:
# python -m pytest packages/recipesql/test/test_crudsql.py -v --log-cli-level=DEBUG
class TestCrudSQL:

    @classmethod
    def setup_class(cls):
        app = Flask(__name__)
        app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///RecipeGrabberTest.db"
        app.app_context().push()

        db = SQLAlchemy(app)

        cls.users = UsersMocks().get_users()
        cls.User = define_user(db)
        cls.crudsql = CrudSQL(db)

        db.drop_all()
        db.create_all()

    @classmethod
    def teardown_class(cls):
        rmtree("instance")

    def test_save_one(self):
        for user in self.users:
            saved_user = self.crudsql.save_one(self.User(**user))
            query_user = self.crudsql.find_one(self.User(**user))

            assert saved_user == query_user

    def test_find_one_by_id(self):
        for user in self.users:
            row = self.User(**user)

            query = self.crudsql.find_one(row)
            query_by_id = self.crudsql.find_one(self.User, query.id)

            assert query_by_id == query

    def test_update_one(self):
        for user in self.users:
            new_user = self.User(**user)
            user[new_user.firstName] = "new_value"

            updated_user = self.crudsql.update_one(new_user, user)
            assert updated_user == self.crudsql.find_one(self.User(**user))

    def test_raise_unique_error_save_one(self):
        for user in self.users:
            pytest.raises(UniqueError,
                          self.crudsql.save_one,
                          self.User(**user))

    def test_raise_column_error_update_one(self):
        for user in self.users:
            pytest.raises(ColumnError, self.crudsql.update_one,
                          self.User(**user),
                          {"none": "none"})

    def test_raise_type_error_update_one(self):
        for user in self.users:
            pytest.raises(Exception,
                          self.crudsql.update_one,
                          self.User(**user),
                          (13, "non", 1.1))

    def test_delete_one(self):
        for user in self.users:
            self.crudsql.delete_one(self.User(**user))
            assert not self.crudsql.find_one(self.User(**user))

    def test_raise_table_error_find_one(self):
        for user in self.users:
            pytest.raises(TableError, self.crudsql.find_one, user)

    def test_raise_unique_error_delete_one(self):
        for user in self.users:
            pytest.raises(UniqueError,
                          self.crudsql.delete_one,
                          self.User(**user))

    def test_unique_error_update_one(self):
        for user in self.users:
            pytest.raises(UniqueError,
                          self.crudsql.update_one,
                          self.User(**user), user)

    def test_raise_table_error_save_one(self):
        for user in self.users:
            pytest.raises(TableError,
                          self.crudsql.save_one,
                          user)
