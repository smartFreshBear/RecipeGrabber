import logging

from data_loader.spreadsheet_dao import *


def get_values(should_print=False, ignore_un_tagged=True, cells_range=None, target_spreadsheet=None):
    if target_spreadsheet or cells_range:
        response = get_spreadsheet_values(cells_range, target_spreadsheet)
    else:
        response = get_spreadsheet_values()

    values = response.get('values', [])

    if not values:
        logging.info('No data found.')
    elif should_print:
        for row in values:
            if len(row) == 3:
                logging.info('%s, %s, %s \n' % (row[0], row[1], row[2]))
    if ignore_un_tagged:
        return [v for v in values if len(v) == 3 and v[1] != '?' and v[2] != '?']
    return values


def insert_values(cells_list, target_spreadsheet):
    request = append_spreadsheet_values(cells_list, target_spreadsheet=target_spreadsheet)

    response = request.execute()

    return response


def delete_values(cells_range, target_spreadsheet):
    request = delete_spreadsheet_values(cells_range=cells_range, target_spreadsheet=target_spreadsheet)

    response = request.execute()

    return response
