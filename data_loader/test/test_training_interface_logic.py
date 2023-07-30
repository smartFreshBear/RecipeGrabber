import unittest

from data_loader.training_storer import get_values, insert_values

TEST_INSERT_SPREADSHEET_ID = '1KQ2nFO9oeDLhHmKh9UTvNnhepKhMuTOyKmh7Nnxbj80'


class TestTrainingInterfaceLogic(unittest.TestCase):
    def test_get_values_data(self):
        values = get_values()
        assert all(isinstance(row, list) for row in values), 'Function returning invalid data'

    def test_get_values_not_empty(self):
        values = get_values()
        assert len(values) != 0, 'Function returned an empty list'

    def test_insert_values(self):
        cells = [['a', 'b', 'c']]

        response = insert_values(cells, TEST_INSERT_SPREADSHEET_ID)

        assert response, 'Request returned bad response'
