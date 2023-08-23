from utils import text_extractor
SIZE_OF_TRAINING_EXAMPLE = 5


class WebsiteIterator:
    def __init__(self, url, caching_manager, section_size):
        self.url = url
        self.content = (text_extractor.get_all_text_from_url(url, caching_manager=caching_manager))[0]
        self.index = 0
        self.content_length = len(self.content)
        self.section_size = section_size

    def next(self):
        lines = self.content.splitlines()
        end_index = self.index + self.section_size
        if end_index >= self.content_length:
            end_index = self.content_length - self.index
        if self.index >= self.content_length:
            raise StopIteration
        else:
            result = lines[self.index:end_index]
            self.index += self.section_size
            return result

    def get_iterator_for_website(url, caching_manager, section_size=SIZE_OF_TRAINING_EXAMPLE):
        return WebsiteIterator(url, caching_manager, section_size)