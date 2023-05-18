import logging
from dataclasses import dataclass
from datetime import datetime
from sqlite3 import IntegrityError

from flask import jsonify


def define_class(db):
    @dataclass
    class BrokenLink(db.Model):
        __table_args__ = {'extend_existing': True}
        id: int = db.Column(db.Integer, primary_key=True)
        url: str = db.Column(db.String(200), unique=True, nullable=False)
        taken_care_of: bool = db.Column(db.Boolean, unique=False, nullable=False)
        date: datetime = db.Column(db.DateTime, unique=False, nullable=True)

    return BrokenLink


class BrokenLinkClient:
    def __init__(self, db):
        self.db = db
        self.BrokenLink = define_class(self.db)

    def presist_broken_link(self, url, taken_care_of):
        BrokenLink = self.BrokenLink
        try:
            self.db.session.add(BrokenLink(url=url, taken_care_of=taken_care_of, date=datetime.now()))
            self.db.create_all()
            self.db.session.commit()
        except IntegrityError:
            logging.error("%s url key already inserted".format(url))

    def get_all_broken_links(self):
        lst = self.BrokenLink.query.all()
        return jsonify(lst)

    def delete_broken_links_by_ids(self, ids):
        for id in ids:
            self.BrokenLink.query.filter(self.BrokenLink.id == id).delete()

        self.db.session.commit()
        return 'ok'
