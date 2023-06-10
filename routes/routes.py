from flask import Blueprint, request

from services.broken_links_service import BrokenLinkService
from services.en_text_extractor_service import EnglishTextExtractorService
from services.text_extractor_service import TextExtractorService
from services.training_service import TrainingService

api_bp = Blueprint('api_bp', __name__)


class Routes:
    def __init__(self, db, executor):
        self.training_service = TrainingService()
        self.en_text_extractor_service = EnglishTextExtractorService()
        self.text_extractor_service = TextExtractorService(db, executor)
        self.broken_links_service = BrokenLinkService(db)

        self.register_routes()

    def register_routes(self):
        @api_bp.route('/train')
        def train(): return self.training_service.train()

        @api_bp.route('/find_recipe_in_text/', methods=['POST'])
        def check_if_text_is_recipe(): return self.text_extractor_service.check_if_text_in_recipe(request.form)

        @api_bp.route('/add_url_to_investigation_list/', methods=['POST'])
        def add_url_to_investigation_list(): return self.broken_links_service.presist_broken_link(request.form, False)

        @api_bp.route('/get_all_broken_links', methods=['GET'])
        def get_all_broken_links(): return self.broken_links_service.get_all_broken_links()

        @api_bp.route('/remove_broken_links_by_ids/', methods=['POST'])
        def remove_broken_links_by_ids(): return self.broken_links_service.delete_broken_links_by_ids(request.form)

        @api_bp.route('/find_recipe_in_url/', methods=['POST'])
        def find_recipe_in_url_window_algo_based(): return self.text_extractor_service.find_recipe_in_url(request.form)

        @api_bp.route('/populate_training_example_from_url/', methods=['POST'])
        def populate_training_example_from_url(): return self.training_service.populate_training(request.form)

        @api_bp.route('/en/find_recipe_in_url/', methods=['POST'])
        def en_find_recipe_in_url_window_algo_based(): return self.en_text_extractor_service.find_recipe_in_url(request.form)
