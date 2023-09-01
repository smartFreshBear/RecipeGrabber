from data_loader.test.test_training_storer_logic import TEST_SPREADSHEET_ID
from training.website_iterator import WebsiteIterator
from data_loader import training_storer


class WebsiteCrawler:
    @staticmethod
    def crawl(url, caching_manager, paragraph_size):
        iterator = WebsiteIterator.get_iterator_for_website(url, caching_manager, paragraph_size)

        # Iterates over the website and then execute multi insertion.
        cells_list = []
        result = iterator.next()
        try:
            while True:
                cells_list.append(result)
                result = iterator.next()
        except StopIteration:
            pass

        # Converts list of strings into one string separated with \n
        reformatted_list = list(map(lambda x: ['\n'.join(x)], cells_list))

        training_storer.insert_values(reformatted_list, target_spreadsheet=TEST_SPREADSHEET_ID)
        return len(reformatted_list)