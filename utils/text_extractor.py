import time
import urllib.request
import urllib.parse
from _socket import timeout

from bs4 import BeautifulSoup
from sqlalchemy.sql.cache_key import NO_CACHE
from w3lib.url import safe_url_string
import logging
import html2text
from flask import current_app

from services.timeout_blacklist_service import increase_timeout_count, in_timeout_blacklist

logging.getLogger('text.extractor')

USER_AGENT = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 11_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'

GOOGLE_CACHE_PREFIX = 'https://webcache.googleusercontent.com/search?q=cache:'

NO_CACHE_STRING = 'cache:https:'


class TextExtractor:

    def __init__(self, caching_manager=None):
        self.caching_manager = caching_manager

    @staticmethod
    def find_title(html):
        soup = BeautifulSoup(html, 'html.parser')
        title = soup.find('title')
        if title is not None:
            logging.debug("title found")
            return title.string
        else:
            title_error_message = "title wasn't found"
            logging.error(title_error_message)
            return title_error_message

    def get_all_text_from_url(self, url, retries=5):

        time_out_secs = current_app.config['URL_TIMEOUT']
        if self.caching_manager and in_timeout_blacklist(url, self.caching_manager):
            logging.error("url timed out too many times and have been blocked, try again later.")
            raise BlockingIOError("The request to this URL has been blocked temporarily")
        if retries == 0:
            logging.error("get_all_text_from_url: could not handle request")
            raise ValueError("could not handle request")
        try:
            url_utf_8 = safe_url_string(url)

            if retries % 2 == 1:
                url_utf_8 = f'{GOOGLE_CACHE_PREFIX}{url_utf_8}'

            headers = {'User-Agent': USER_AGENT}
            request = urllib.request.Request(url_utf_8, None, headers)

            response = urllib.request.urlopen(request, timeout=time_out_secs)
            if response.status == 404:
                raise Exception('website not found')
            given_encoding = response.headers.get_content_charset()
            encoding = 'utf-8' if given_encoding is None else given_encoding
            html = response.read().decode(encoding)

            h = html2text.HTML2Text()
            h.ignore_links = False
            h.ignore_images = True
            title = TextExtractor.find_title(html)
            if NO_CACHE_STRING in title:
                raise Exception('website not found in google cache')
            allText = h.handle(html)

            return allText, title
        except timeout as exc:
            logging.error(
                "an exception occurred while trying to access url {} trying again \n more details: {}".format(url, exc))
            time.sleep(1)
            retries = retries - 1
            if retries == 0:
                increase_timeout_count(url, self.caching_manager)
                raise timeout("The request to the URL has timed out.")
            return self.get_all_text_from_url(url, retries)
        except Exception as exc:
            if retries > 0:
                logging.error(
                    "an exception occurred while trying to access url {} trying again \n more details: {}".format(url,
                                                                                                                  exc))
                time.sleep(3)
                retries = retries - 1
                return self.get_all_text_from_url(url, retries)
            else:
                raise
