from utils import text_extractor
DEFAULT_PARA_SIZE = 5


class WebsiteIterator:
    def __init__(self, url, caching_manager, paragraph_size):
        self.url = url
        self.content = (text_extractor.get_all_text_from_url(url, caching_manager=caching_manager))[0]
        self.index = 0
        self.content_length = len(self.content)
        self.paragraph_size = paragraph_size


    def next(self):
        lines = self.content.splitlines()
        if self.index == 0:
            self.content_length = len(lines)
        end_index = min(self.content_length, self.index+self.paragraph_size)
        if self.index >= self.content_length:
            raise StopIteration
        else:
            result = lines[self.index:end_index]
            if len(result) == 0:
                raise StopIteration
            self.index += self.paragraph_size
            return result

    def get_iterator_for_website(url, caching_manager, paragraph_size=DEFAULT_PARA_SIZE):
        return WebsiteIterator(url, caching_manager, paragraph_size)