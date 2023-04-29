from utils import text_extractor
SIZE_OF_TRAINING_EXAMPLE = 5


class WebsiteIterator:
    def __init__(self, url):
        self.url = url
        self.content = self.get_website_text()
        self.index = 0
        self.content_length = len(self.content)

    def get_website_text(self):
        allText,title = text_extractor.get_all_text_from_url(self.url)
        return allText

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

def get_iterator_for_website(url):
    return WebsiteIterator(url)
