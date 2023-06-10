import traceback

from flask import jsonify

import main_flow


class TrainingService:
    def __init__(self):
        pass

    @staticmethod
    def train():
        try:
            return main_flow.main_flow.main()
        except RuntimeError as exc:
            traceback.print_exc()
            print(exc)

    @staticmethod
    def populate_training(form):
        password = form.get('password')

        if password != "toy_password":
            return jsonify({'error': 'Invalid password'}), 401

        return jsonify({'status': 'OK'}), 200
