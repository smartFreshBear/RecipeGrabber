from flask import Flask
from flask_sqlalchemy import SQLAlchemy


class DataBase:
    def __init__(self, app):
        app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///recipeGrabber.sqlite"
        app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
        self.db = SQLAlchemy(app)

    def get_db_instance(self):
        return self.db
