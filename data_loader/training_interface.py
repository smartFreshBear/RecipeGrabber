import logging

from data_loader.training_extractor import *


def load_all_training_examples(should_print=False, ignore_un_tagged=True):
    values = request_to_get_spreadsheet_values()

    if not values:
        logging.info('No data found.')
    elif should_print:
        for row in values:
            if len(row) == 3:
                logging.info('%s, %s, %s \n' % (row[0], row[1], row[2]))
    if ignore_un_tagged:
        return [v for v in values if len(v) == 3 and v[1] != '?' and v[2] != '?']
    return values


def insert_data_to_training(cells_list, from_cell, to_cell):
    def from_cell_row_str_row(row):
        return list(map(lambda c: c.text, row))

    rows = list(map(from_cell_row_str_row, cells_list))

    request = request_to_append_spreadsheet_values(rows, from_cell, to_cell)

    response = request.execute()

    return response is not None
