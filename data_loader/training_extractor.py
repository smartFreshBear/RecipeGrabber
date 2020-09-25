from __future__ import print_function
import pickle
import os.path
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
import utils.textExtractor

# If modifying these scopes, delete the file token.pickle.
PATH_TO_CRED = 'D:\\ML\\RecipeGrabber\\data_loader\\resources\client_secret.json'
SCOPES = ['https://www.googleapis.com/auth/spreadsheets']

# The ID and range of a sample spreadsheet.
SAMPLE_SPREADSHEET_ID = '1NGRUyzImlaUd-UrTkNXSd1JB7OOHnw6e1h4AohRXFK8'

SAMPLE_RANGE_NAME = 'A:C'

""" TODO address + sheets from training set"""


def load_all_training_examples(should_print = False, ignore_un_tagged = True):
    service = get_clinet_to_training_set()

    # Call the Sheets API
    sheet = service.spreadsheets()
    result = sheet.values().get(spreadsheetId=SAMPLE_SPREADSHEET_ID,
                                range=SAMPLE_RANGE_NAME).execute()
    values = result.get('values', [])

    if not values:
        print('No data found.')
    elif should_print:
        for row in values:
            if len(row) == 3:
                print('%s, %s, %s \n' % (row[0], row[1], row[2]))
    if ignore_un_tagged:
        return [v for v in values if len(v) == 3 and v[1] != '?' and v[2] != '?']
    return values


def get_clinet_to_training_set():
    """Shows basic usage of the Sheets API.
    Prints values from a sample spreadsheet.
    """
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
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                PATH_TO_CRED, SCOPES)
            creds = flow.run_local_server(port=58326)
        # Save the credentials for the next run
        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)
    service = build('sheets', 'v4', credentials=creds)
    return service


def populate_training_from_urls(url_list):
    for url in url_list:

        text_lst = utils.textExtractor.get_text_from_url(url)

        clinet = get_clinet_to_training_set()

        values_to_db = [[text, '?', '?'] for text in text_lst]


        body = {
            'values': values_to_db
        }

        request = clinet.spreadsheets().values().append(spreadsheetId=SAMPLE_SPREADSHEET_ID,
                                                         range=SAMPLE_RANGE_NAME,
                                                         valueInputOption='RAW',
                                                         insertDataOption='INSERT_ROWS',
                                                         body=body)
        response = request.execute()

        print('{0} cells appended.'.format(response \
                                           .get('updates') \
                                           .get('updatedCells')))



if __name__ == '__main__':
    my_file_handle = open("D:\\ML\\RecipeGrabber\\data_loader\\resources\\urls.txt", encoding='utf-8')
    url_lst = my_file_handle.read().split('\n')
    populate_training_from_urls(url_lst)
