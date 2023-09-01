import unittest
from unittest.mock import patch
from training.website_iterator import WebsiteIterator
from daos.caching_manager import CachingManager
from flask import Flask


class TestWebsiteIterator(unittest.TestCase):
    def setUp(self):
        self.app = Flask(__name__)
        self.app.config['URL_TIMEOUT'] = 10
        self.app_context = self.app.app_context()
        self.app_context.push()
        self.temp_caching_manager = CachingManager()  # A cache for the test

        self.url = "www.nothing.com"
        self.mocked_website_text = 'Line1a Line1b Line1c Line1d, Line1e, Line1f.\n' \
                                   'Line2a Line2b Line2c Line2d, Line2e, Line2f.\n' \
                                   'Line3a, Line3b Line3c Line3d, Line3e, Line3f.\n' \
                                   'Line4a Line4b Line4c Line1d, Line4e, Line4f.\n' \
                                   'Line5a Line5b. Line5c, Line5d, Line5e Line5f.\n'
        self.website_title = "Website title"
        self.mocked_lines = self.mocked_website_text.splitlines()

    def test_next_full_content(self):
        with patch('utils.text_extractor.get_all_text_from_url') as mock_get_all_text:
            mock_get_all_text.return_value = [self.mocked_website_text, self.website_title]
            iterator = WebsiteIterator.get_iterator_for_website(self.url, caching_manager=self.temp_caching_manager)
            result = iterator.next()
            expected_result = [self.mocked_lines[0], self.mocked_lines[1],self.mocked_lines[2],self.mocked_lines[3],self.mocked_lines[4]]
            self.assertEqual(result, expected_result)

            try:
                result = iterator.next()
            except StopIteration:
                self.assertTrue(True)
            else:
                self.fail("Expected StopIteration but got a result: {}".format(result))

    def test_next_partial_content(self):
        self.mocked_website_text = "\n".join(self.mocked_lines[:3])

        with patch('utils.text_extractor.get_all_text_from_url') as mock_get_website_text:
            mock_get_website_text.return_value = [self.mocked_website_text, self.website_title]
            iterator = WebsiteIterator.get_iterator_for_website(self.url, caching_manager=self.temp_caching_manager)
            result = iterator.next()
            self.assertEqual(result, [self.mocked_lines[0], self.mocked_lines[1], self.mocked_lines[2]])

            try:
                result = iterator.next()
            except StopIteration:
                self.assertTrue(True)
            else:
                self.fail("Expected StopIteration but got a result: {}".format(result))

    def test_next_one_line_content(self):
        self.mocked_website_text = "\n".join(self.mocked_lines[:1])
        with patch('utils.text_extractor.get_all_text_from_url') as mock_get_website_text:
            mock_get_website_text.return_value = [self.mocked_website_text, self.website_title]
            iterator = WebsiteIterator.get_iterator_for_website(self.url, caching_manager=self.temp_caching_manager)
            result = iterator.next()
            expected_result = [self.mocked_lines[0]]
            self.assertEqual(result, expected_result)

            try:
                result = iterator.next()
            except StopIteration:
                self.assertTrue(True)
            else:
                self.fail("Expected StopIteration but got a result: {}".format(result))

    def test_next_empty_content(self):
        self.mocked_website_text = ''
        with patch('utils.text_extractor.get_all_text_from_url') as mock_get_website_text:
            mock_get_website_text.return_value = [self.mocked_website_text, self.website_title]
            iterator = WebsiteIterator.get_iterator_for_website(self.url, caching_manager=self.temp_caching_manager)
            with self.assertRaises(StopIteration):
                iterator.next()

    if __name__ == '__main__':
        unittest.main()