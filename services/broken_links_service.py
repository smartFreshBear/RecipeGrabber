from datetime import datetime
from flask import jsonify

from daos.models.brokenlinks.broken_link_model import define_broken_link


class BrokenLinkService:
    def __init__(self, crud):
        self.crud = crud
        self.BrokenLink = define_broken_link(crud.db)

    def presist_broken_link(self, form, taken_care_of):
        url = form['url']
        try:
            self.crud.save_one(self.BrokenLink(url=url,
                                                 taken_care_of=taken_care_of,
                                                 date=datetime.now()))
            return jsonify({'status': 'OK'})
        except Exception:
            return jsonify({'status': 'ERROR'}), 500

    def get_all_broken_links(self):
        return jsonify(self.crud.find_all(self.BrokenLink))

    def delete_broken_links_by_ids(self, form):
        ids_strs = form.get("ids", "")
        ids = list(map(lambda id_str: int(id_str), ids_strs.split(',')))
        for id in ids:
            self.crud.delete_one(self.BrokenLink, id)

        return jsonify({'status': 'OK'})
