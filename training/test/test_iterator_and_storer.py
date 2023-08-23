import unittest
from training.website_iterator import WebsiteIterator
from data_loader import training_storer
from training.site_capture import SiteCapture
from daos.caching_manager import CachingManager
from flask import Flask

SIZE_OF_TRAINING_EXAMPLE = 5

class TestIteratorAndStorer(unittest.TestCase):
    def setUp(self):
        self.app = Flask(__name__)
        self.app.config['URL_TIMEOUT'] = 10
        self.app_context = self.app.app_context()
        self.app_context.push()
        self.temp_caching_manager = CachingManager()  # A cache for the test

        self.test_spreadsheet_id = '1KQ2nFO9oeDLhHmKh9UTvNnhepKhMuTOyKmh7Nnxbj80'
        self.test_link = "https://food.walla.co.il/recipe/641210"

    def test_basic_extract_and_store(self):
        original_spreadsheet = training_storer.get_values(cells_range='A:C', target_spreadsheet=self.test_spreadsheet_id)
        added_cells_count = SiteCapture.capture(self.test_link, caching_manager=self.temp_caching_manager, section_size=SIZE_OF_TRAINING_EXAMPLE)
        updated_spreadsheet = training_storer.get_values(cells_range='A:C', target_spreadsheet=self.test_spreadsheet_id)

        # Suppose it's enough to compare the first rows and the last rows
        assert len(updated_spreadsheet) == len(original_spreadsheet) + added_cells_count, "Spreadsheet length mismatch"
        assert original_spreadsheet[0] == updated_spreadsheet[0] and original_spreadsheet[
            original_spreadsheet.length - 1] == updated_spreadsheet[
                   original_spreadsheet.length - 1], "First rows or last rows don't match"

        counter = 0
        iterator = WebsiteIterator.get_iterator_for_website(self.test_link)
        result = iterator.next()
        while result is not StopIteration:
            assert updated_spreadsheet[original_spreadsheet + counter] == result, "Spreadsheet content mismatch"
        training_storer.delete_values(cells_range='A:C', target_spreadsheet=self.test_spreadsheet_id)


if __name__ == '__main__':
    unittest.main()