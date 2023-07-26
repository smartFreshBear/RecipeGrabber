from daos.caching_manager import CachingManager
from utils import text_extractor
SIZE_OF_TRAINING_EXAMPLE = 5

class TrainingPopulation:
    def __init__(self, url):
        self.url = url
        self.content = self.get_website_text(url)
        self.index = 0
        self.content_length = len(self.content)

    @staticmethod
    def get_website_text(url):
        all_text = ''
        caching_manager = CachingManager()
        all_text = text_extractor.get_all_text_from_url(url, caching_manager)
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

def get_iterator_for_website(url):
    return TrainingPopulation(url)