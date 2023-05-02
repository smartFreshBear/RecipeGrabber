from utils import text_extractor
import validators
from unittest import TestCase

SIZE_OF_TRAINING_EXAMPLE = 5


class WebsiteIterator:
    def __init__(self, url):
        self.url = url
        self.content = self.get_website_text()
        self.index = 0
        self.content_length = len(self.content)

    def get_website_text(self):
        all_text = ''
        if self.is_website_url(self.url):
            all_text, title = text_extractor.get_all_text_from_url(self.url)
        else:
            all_text = self.url
        return all_text

    def next(self):
        lines = self.content.splitlines()
        copy_from = self.index + SIZE_OF_TRAINING_EXAMPLE
        if copy_from >= self.content_length:
            copy_from = self.content_length - self.index
        if self.index >= self.content_length:
            raise StopIteration
        else:
            result = lines[self.index:copy_from]
            self.index += SIZE_OF_TRAINING_EXAMPLE
            return result

    def is_website_url(self, url):
        if validators.url(url):
            parsed_url = validators.url(url)
            if parsed_url.scheme in ['http', 'https'] and parsed_url.hostname:
                return True
        return False


def get_iterator_for_website(url):
    return WebsiteIterator(url)





