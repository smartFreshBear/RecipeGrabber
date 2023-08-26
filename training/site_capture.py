from training.website_iterator import WebsiteIterator
from data_loader import training_storer

TEST_SPREADSHEET_ID = '1KQ2nFO9oeDLhHmKh9UTvNnhepKhMuTOyKmh7Nnxbj80'


class SiteCapture:
    @staticmethod
    def capture(url, caching_manager, section_size):
        iterator = WebsiteIterator.get_iterator_for_website(url, caching_manager, section_size)

        # Iterates over the website and then execute multi insertion.
        cells_list = []
        result = iterator.next()
        try:
            while True:
                result = iterator.next()
                cells_list.append(result)
        except StopIteration:
            pass

        reformatted_list = list(map(lambda x: ['\n'.join(x)], cells_list))

        training_storer.insert_values(reformatted_list, target_spreadsheet=TEST_SPREADSHEET_ID)
        return len(cells_list)