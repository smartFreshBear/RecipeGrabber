import unittest
from data_loader.test.test_training_storer_logic import TEST_SPREADSHEET_ID
from training.website_iterator import WebsiteIterator
from data_loader import training_storer
from training.website_crawler import WebsiteCrawler
from daos.caching_manager import CachingManager
from flask import Flask

DEFAULT_PARA_SIZE = 5


class TestWebsiteCrawler(unittest.TestCase):
    def setUp(self):
        self.app = Flask(__name__)
        self.app.config['URL_TIMEOUT'] = 10
        self.app_context = self.app.app_context()
        self.app_context.push()
        self.temp_caching_manager = CachingManager()  # A cache for the test

        self.test_link = "https://www.10dakot.co.il/recipe/%D7%9E%D7%AA%D7%9B%D7%95%D7%9F-%D7%9C%D7%A4%D7%A0%D7%A7%D7%99%D7%99%D7%A7/"

    def test_crawler(self):
        original_spreadsheet = training_storer.get_values(ignore_un_tagged=False, cells_range='A:A', target_spreadsheet=TEST_SPREADSHEET_ID)
        added_cells_count = WebsiteCrawler.crawl(self.test_link, caching_manager=self.temp_caching_manager,
                                              paragraph_size=DEFAULT_PARA_SIZE)
        updated_spreadsheet = training_storer.get_values(ignore_un_tagged=False, cells_range='A:A', target_spreadsheet=TEST_SPREADSHEET_ID)

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
        finally:
            training_storer.delete_values(cells_range='A6:A', target_spreadsheet=TEST_SPREADSHEET_ID)


if __name__ == '__main__':
    unittest.main()