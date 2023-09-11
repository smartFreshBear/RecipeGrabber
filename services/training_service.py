import traceback

from flask import jsonify
from training.website_crawler import WebsiteCrawler

import main_flow


class TrainingService:
    def __init__(self, caching_manager):
        self.caching_manager = caching_manager

    @staticmethod
    def train():
        try:
            return main_flow.main_flow.main()
        except RuntimeError as exc:
            traceback.print_exc()
            print(exc)

    def populate_training(self, request):
        username = request.headers.get('username')
        password = request.headers.get('password')
        url = request.form.get('url')

        if username != 'username' or password != 'password':
            return jsonify({'error': 'Wrong username or password'}), 401

        if not url:
            return jsonify({'error': 'Url not provided'}), 400

        length = WebsiteCrawler.crawl(url, self.caching_manager, 5)

        return jsonify({'message': 'Success! {} lines added.'.format(length), 'status': 'OK'}), 200
