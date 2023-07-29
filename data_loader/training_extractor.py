from __future__ import print_function

import os.path
import pickle

from google.auth.transport.requests import Request
from googleapiclient.discovery import build

from utils.logger import create_logger_instance

# If modifying these scopes, delete the file token.pickle.
SCOPES = ['https://www.googleapis.com/auth/spreadsheets']

# The ID and range of a sample spreadsheet.
SAMPLE_SPREADSHEET_ID = '1NGRUyzImlaUd-UrTkNXSd1JB7OOHnw6e1h4AohRXFK8'
TEST_INSERT_SPREADSHEET_ID = '1KQ2nFO9oeDLhHmKh9UTvNnhepKhMuTOyKmh7Nnxbj80'

SAMPLE_RANGE_NAME = 'A:C'

training_extractor_logger = create_logger_instance('Training_Extractor')

""" TODO address + sheets from training set"""


def get_values_resource():
    service = get_client_to_training_set()
    sheet = service.spreadsheets()
    values = sheet.values()

    return values


def request_to_get_spreadsheet_values():
    resource = get_values_resource()
    result = resource.get(spreadsheetId=SAMPLE_SPREADSHEET_ID,
                          range=SAMPLE_RANGE_NAME).execute()
    values = result.get('values', [])
    return values


def request_to_append_spreadsheet_values(values, from_cell, to_cell):
    resource = get_values_resource()
    body = {
        'values': values
    }
    request = resource.append(spreadsheetId=TEST_INSERT_SPREADSHEET_ID,
                              range='{}:{}'.format(from_cell, to_cell),
                              valueInputOption='RAW',
                              insertDataOption='OVERWRITE',
                              body=body)

    return request


def get_client_to_training_set():
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
