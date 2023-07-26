from __future__ import print_function

import logging
import os.path
import pickle

from google.auth.transport.requests import Request
from googleapiclient.discovery import build

# If modifying these scopes, delete the file token.pickle.
SCOPES = ['https://www.googleapis.com/auth/spreadsheets']

# The ID and range of a sample spreadsheet.
SAMPLE_SPREADSHEET_ID = '1NGRUyzImlaUd-UrTkNXSd1JB7OOHnw6e1h4AohRXFK8'
TEST_INSERT_SPREADSHEET_ID = '1KQ2nFO9oeDLhHmKh9UTvNnhepKhMuTOyKmh7Nnxbj80'

SAMPLE_RANGE_NAME = 'A:C'

""" TODO address + sheets from training set"""


def get_values_resource():
    service = get_clinet_to_training_set()
    sheet = service.spreadsheets()
    values = sheet.values()

    return values


def request_to_get_spreadsheet_values():
    resource = get_values_resource()
    result = resource.get(spreadsheetId=SAMPLE_SPREADSHEET_ID,
                              range=SAMPLE_RANGE_NAME).execute()
    values = result.get('values', [])
    return values


def load_all_training_examples(should_print=False, ignore_un_tagged=True):
    # service = get_clinet_to_training_set()
    #
    # # Call the Sheets API
    # sheet = service.spreadsheets()
    # result = sheet_values.get(spreadsheetId=SAMPLE_SPREADSHEET_ID,
    #                           range=SAMPLE_RANGE_NAME).execute()
    # values = result.get('values', [])

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


def get_clinet_to_training_set():
    creds = None
    # The file token.pickle stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            creds = pickle.load(token)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        # Save the credentials for the next run
        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)
    service = build('sheets', 'v4', credentials=creds)
    return service
