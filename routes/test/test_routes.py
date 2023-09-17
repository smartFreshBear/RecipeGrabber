import unittest
from flask import Flask

from daos.caching_manager import CachingManager
from routes.routes import Routes, api_bp
from services.training_service import TrainingService


def get_flask_client():
    app = Flask(__name__)
    app.config.from_pyfile('test_config.py')
    caching_manager = CachingManager()

    with app.app_context():
        Routes.register_training_route(TrainingService(caching_manager))
        app.register_blueprint(api_bp)

    return app.test_client()


class TestRoutes(unittest.TestCase):
    def setUp(self):
        self.client = get_flask_client()
        self.mock_url = 'https://heninthekitchen.com/blog/2021/06/02/%D7%A1%D7%97%D7%95%D7%92/'
        self.mock_username = 'username'
        self.mock_password = 'password'

    def test_train_from_url(self):
        response = self.client.post('/populate_training',
                                    headers={
                                        'username': self.mock_username,
                                        'password': self.mock_password
                                    },
                                    data={
                                        'url': self.mock_url
                                    })
        assert response.status_code == 200


if __name__ == '__main__':
    unittest.main()
