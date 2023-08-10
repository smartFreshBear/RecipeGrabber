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

SAMPLE_RANGE_NAME = 'A:C'



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


def get_values_resource():
    service = get_client_to_training_set()
    sheet = service.spreadsheets()
    values = sheet.values()

    return values


def get_spreadsheet_values(cells_range=SAMPLE_RANGE_NAME, target_spreadsheet=SAMPLE_SPREADSHEET_ID):
    resource = get_values_resource()
    response = resource.get(spreadsheetId=target_spreadsheet,
                            range=cells_range).execute()
    return response


def append_spreadsheet_values(values, cells_range=SAMPLE_RANGE_NAME, target_spreadsheet=SAMPLE_SPREADSHEET_ID):
    resource = get_values_resource()
    body = {
        'values': values
    }
    request = resource.append(spreadsheetId=target_spreadsheet,
                              range=cells_range,
                              valueInputOption='RAW',
                              insertDataOption='OVERWRITE',
                              body=body)

    return request


def delete_spreadsheet_values(cells_range: list, target_spreadsheet):
    resource = get_values_resource()
    body = {
        'ranges': cells_range
    }
    request = resource.batchClear(spreadsheetId=target_spreadsheet,
                                  body=body)

    return request
