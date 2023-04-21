import unittest

from flask import Flask

from utils.text_extractor import get_all_text_from_url

app = Flask(__name__)
app.config['URL_TIMEOUT'] = 10
app.app_context().push()


class TestTextExtractorLogic(unittest.TestCase):
    def test_text_extractor_timeout(self):
        url = 'https://postman-echo.com/delay/11'
        with self.assertRaises(Exception):
            get_all_text_from_url(url)

    def test_text_extractor_threshold(self):
        url = 'https://postman-echo.com/delay/9'
        try:
            get_all_text_from_url(url)
        except Exception:
            self.fail("raised ExceptionType unexpectedly!")
