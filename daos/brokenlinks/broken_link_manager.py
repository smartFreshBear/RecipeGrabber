from dataclasses import dataclass
from datetime import datetime
from sqlite3 import IntegrityError

from flask import jsonify
from flask_sqlalchemy import SQLAlchemy


def define_class(db):
    @dataclass
    class BrokenLink(db.Model):
        __table_args__ = {'extend_existing': True}
        id: int = db.Column(db.Integer, primary_key=True)
        url: str = db.Column(db.String(200), unique=True, nullable=False)
        taken_care_of :bool = db.Column(db.Boolean, unique=False, nullable=False)
        date : datetime = db.Column(db.DateTime, unique=False, nullable=True)

    return BrokenLink

class BrokenLinkClient:

    def __init__(self, app):
        app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///recipeGrabber.sqlite"
        app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
        self.db = SQLAlchemy(app)
        self.db.create_all()



    def presist_broken_link(self, url, taken_care_of):
        BrokenLink = define_class(self.db)
        try:
            self.db.session.add(BrokenLink(url=url, taken_care_of= taken_care_of, date= datetime.now()))
            self.db.create_all()
            self.db.session.commit()
        except IntegrityError:
            print("%s url key already inserted".format(url))



    def get_all_broken_links(self):
        BrokenLink = define_class(self.db)
        lst = BrokenLink.query.all()
        return jsonify(lst)


