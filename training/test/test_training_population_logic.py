from unittest import TestCase
from training.training_population import get_iterator_for_website


class TestTrainingPopulationLog(TestCase):

    def test_next_five_lines(self):
        text = 'Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore\n' \
               'et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut\n' \
               'aliquip ex ea commodo consequat. Duis aute irure dolor in reprehenderit in\n' \
               'voluptate velit esse cillum dolore eu fugiat nulla pariatur. Excepteur sint occaecat cupidatat\n' \
               'non proident, sunt in culpa qui officia deserunt mollit anim id est laborum\n' \
               'Sed ut perspiciatis unde omnis iste natus error sit voluptatem accusantium doloremque laudantium,\n'

        iterator = get_iterator_for_website(text)
        result = iterator.next()

        assert ['Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore',
                'et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut',
                'aliquip ex ea commodo consequat. Duis aute irure dolor in reprehenderit in',
                'voluptate velit esse cillum dolore eu fugiat nulla pariatur. Excepteur sint occaecat cupidatat',
                'non proident, sunt in culpa qui officia deserunt mollit anim id est laborum'] == result


    # here checking if the 6'th line is recieved
    def test_next_after_next(self):
        text = 'Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore\n' \
               'et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut\n' \
               'aliquip ex ea commodo consequat. Duis aute irure dolor in reprehenderit in\n' \
               'voluptate velit esse cillum dolore eu fugiat nulla pariatur. Excepteur sint occaecat cupidatat\n' \
               'non proident, sunt in culpa qui officia deserunt mollit anim id est laborum\n' \
               'Sed ut perspiciatis unde omnis iste natus error sit voluptatem accusantium doloremque laudantium,\n'

        iterator = get_iterator_for_website(text)
        result = iterator.next()
        result = iterator.next()

        assert ['Sed ut perspiciatis unde omnis iste natus '
                'error sit voluptatem accusantium doloremque laudantium,'] == result


    def test_one_line_only(self):
        text = 'Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore'

        iterator = get_iterator_for_website(text)
        result = iterator.next()

        assert ['Lorem ipsum dolor sit amet, consectetur adipiscing elit, '
                'sed do eiusmod tempor incididunt ut labore'] == result

    def test_empty_text(self):
        text = ''

        iterator = get_iterator_for_website(text)
        result = iterator.next()

        assert '' == result

