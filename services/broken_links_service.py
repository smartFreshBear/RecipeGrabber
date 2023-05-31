import logging
from datetime import datetime
from sqlite3 import IntegrityError

from flask import jsonify

from daos.models.brokenlinks.broken_link_model import define_broken_link


class BrokenLinkService:
    def __init__(self, db):
        self.db = db
        self.BrokenLink = define_broken_link(self.db)

    def presist_broken_link(self, form, taken_care_of):
        url = form['url']
        try:
            self.db.session.add(self.BrokenLink(url=url, taken_care_of=taken_care_of, date=datetime.now()))
            self.db.create_all()
            self.db.session.commit()
            return jsonify({'status': 'OK'})
        except IntegrityError:
            logging.error("%s url key already inserted".format(url))

    def get_all_broken_links(self):
        lst = self.BrokenLink.query.all()
        return jsonify(lst)

    def delete_broken_links_by_ids(self, form):
        ids_strs = form['ids']
        ids = list(map(lambda id_str: int(id_str), ids_strs.split(',')))
        for id in ids:
            self.BrokenLink.query.filter(self.BrokenLink.id == id).delete()

        self.db.session.commit()
        return jsonify({'status': 'OK'})
