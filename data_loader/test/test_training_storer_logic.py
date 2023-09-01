import unittest

from data_loader.training_storer import get_values, insert_values, delete_values

TEST_SPREADSHEET_ID = '1KQ2nFO9oeDLhHmKh9UTvNnhepKhMuTOyKmh7Nnxbj80'


class TestTrainingInterfaceLogic(unittest.TestCase):
    def test_get_values_data(self):
        values = get_values(cells_range='A:C', target_spreadsheet=TEST_SPREADSHEET_ID)
        assert all(isinstance(row, list) for row in values), 'Function returning invalid data'

    def test_get_values_not_empty(self):
        values = get_values(cells_range='A:C', target_spreadsheet=TEST_SPREADSHEET_ID)
        assert len(values) != 0, 'Function returned an empty list'

    def test_insert_values(self):
        cells = [['a', 'b', 'c']]

        insert_response = insert_values(cells, TEST_SPREADSHEET_ID)

        assert insert_response is not None, 'Request returned bad response'

        cells_range = insert_response['updates']['updatedRange']
        values = get_values(cells_range=cells_range, target_spreadsheet=TEST_SPREADSHEET_ID)

        assert values == cells

        delete_response = delete_values(cells_range, TEST_SPREADSHEET_ID)

        assert delete_response['clearedRanges'] == [cells_range]
