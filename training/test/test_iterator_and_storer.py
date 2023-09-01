import unittest
from data_loader.test.test_training_storer_logic import TEST_SPREADSHEET_ID
from training.website_iterator import WebsiteIterator
from data_loader import training_storer
from training.website_crawler import WebsiteCrawler
from daos.caching_manager import CachingManager
from flask import Flask

DEFAULT_PARA_SIZE = 5


class TestIteratorAndStorer(unittest.TestCase):
    def setUp(self):
        self.app = Flask(__name__)
        self.app.config['URL_TIMEOUT'] = 10
        self.app_context = self.app.app_context()
        self.app_context.push()
        self.temp_caching_manager = CachingManager()  # A cache for the test

        self.test_link = "https://food.walla.co.il/recipe/641210"


    def test_extract_and_store(self):
        original_spreadsheet = training_storer.get_values(cells_range='A:A', target_spreadsheet=TEST_SPREADSHEET_ID)
        added_cells_count = WebsiteCrawler.crawl(self.test_link, caching_manager=self.temp_caching_manager,
                                              paragraph_size=DEFAULT_PARA_SIZE)
        updated_spreadsheet = training_storer.get_values(cells_range='A:A', target_spreadsheet=TEST_SPREADSHEET_ID)

        # Suppose it's enough to compare the first rows and the last rows
        assert len(updated_spreadsheet) == len(original_spreadsheet) + added_cells_count, "Spreadsheet length mismatch"
        assert original_spreadsheet[0] == updated_spreadsheet[0] and original_spreadsheet[
            len(original_spreadsheet)-1] == updated_spreadsheet[
                   len(original_spreadsheet) - 1], "First rows or last rows don't match"

        counter = 0
        iterator = WebsiteIterator.get_iterator_for_website(self.test_link, caching_manager=self.temp_caching_manager, paragraph_size=DEFAULT_PARA_SIZE)

        result = iterator.next()
        try:
            while True:
                reformatted = '\n'.join(result)
                assert updated_spreadsheet[len(original_spreadsheet) + counter][0] == reformatted, "Spreadsheet content mismatch"
                counter += 1
                result = iterator.next()
        except:
            pass

        training_storer.delete_values(cells_range='A6:A', target_spreadsheet=TEST_SPREADSHEET_ID)


if __name__ == '__main__':
    unittest.main()