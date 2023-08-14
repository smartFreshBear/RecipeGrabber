from shutil import rmtree
import pytest

from flask_sqlalchemy import SQLAlchemy
from flask import Flask

from daos.models.users.user_model import define_user
from plg_packages.plg_dbs.test.users_mocks import UsersMocks
from plg_packages.plg_dbs.plg_postgresql import PLGPostgreSQL
from plg_packages.plg_dbs.dbs_utils.dbs_errors \
import ColumnError, TableError, UniqueError

# Run the test by calling:
# python -m pytest plg_packages/plg_dbs/test/test_plg_db.py -v --log-cli-level=DEBUG
class TestPlgDb:
    
    @classmethod
    def setup_class(cls):
        app = Flask(__name__)
        app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///RecipeGrabberTest.db"
        app.app_context().push()

        db = SQLAlchemy(app)

        cls.users = UsersMocks().get_users()
        cls.User = define_user(db)
        cls.plg_db = PLGPostgreSQL(db)

        db.drop_all()
        db.create_all()

    @classmethod
    def teardown_class(cls):
        rmtree("instance")

    def test_save_one(self):
        for user in self.users:
            saved_user = self.plg_db.save_one(self.User(**user))
            assert saved_user == self.plg_db.find_one(self.User(**user))[0]

    def test_update_one(self):
        for user in self.users:
            new_user = self.User(**user)
            user[new_user.firstName] = "new_value"

            updated_user = self.plg_db.update_one(new_user, user)
            assert updated_user == self.plg_db.find_one(self.User(**user))[0]

    def test_raise_unique_error_save_one(self):
        for user in self.users:
            pytest.raises(UniqueError, self.plg_db.save_one, self.User(**user))

    def test_raise_column_error_update_one(self):
        for user in self.users:
            pytest.raises(ColumnError, self.plg_db.update_one, self.User(**user), 
                          {"none": "none"})

    def test_raise_type_error_update_one(self):
        for user in self.users:
            pytest.raises(Exception, self.plg_db.update_one, self.User(**user), 
                          (13, "non", 1.1))

    def test_delete_one(self):
        for user in self.users:
            self.plg_db.delete_one(self.User(**user))
            assert not self.plg_db.find_one(self.User(**user))[0]


    def test_raise_table_error_find_one(self):
        for user in self.users:
            pytest.raises(TableError, self.plg_db.find_one, user)


    def test_raise_unique_error_delete_one(self):
        for user in self.users:
            pytest.raises(UniqueError, self.plg_db.delete_one, self.User(**user))


    def test_unique_error_update_one(self):
        for user in self.users:
            pytest.raises(UniqueError, self.plg_db.update_one, self.User(**user), user)


    def test_raise_table_error_save_one(self):
        for user in self.users:
            pytest.raises(TableError, self.plg_db.save_one, user)
