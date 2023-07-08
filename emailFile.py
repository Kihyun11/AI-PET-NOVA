import os
import pickle
import os.path
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials
from googleapiclient.errors import HttpError

# Define the Gmail API scopes

def list_emails(service):

    results = service.users().messages().list(userId='me', maxResults=10).execute()
    messages = results.get('messages', [])
    if not messages:
        print('No messages found.')
    else:
        print('Message snippets:')
        for message in messages:
            msg = service.users().messages().get(userId='me', id=message['id']).execute()
            print(msg['snippet'])

#list_emails()

#get recent emails function Y
#read emails: so that we can read new emails
#reply to emails
#send emails



def getService():
    """Shows basic usage of the Gmail API.
    Lists the user's Gmail labels.
    """
    creds = None
    SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']
    # The file token.json stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open('token.json', 'w') as token:
            token.write(creds.to_json())

   # try:
        # Call the Gmail API
    service = build('gmail', 'v1', credentials=creds)
    return service

def getNewEmails(service, prevTime):#change so that it instead checks the last time it checked the email (see api page)
    SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']
    #returns the new emails since we have last checked/unread?
    # Request the list of messages (emails) from the Gmail API
    #service = getService()
    results = service.users().messages().list(userId='me', labelIds=['INBOX'], q=f'after:{prevTime}').execute()
    messages = results.get('messages', [])
    for message in messages:
        #if service.users().messages().q == "unread":
        email = service.users().messages().get(userId='me', id=message['id']).execute()
        headers = email.get('payload', {}).get('headers', [])
            
        subject = next((header['value'] for header in headers if header['name'] == 'Subject'), None)
        sender = next((header['value'] for header in headers if header['name'] == 'From'), None)
        if 'UNREAD' in email['labelIds']:
            print("You have a new email.")
            print(f'Subject: {subject}')
            print(f'from: {sender}')
        else:
            print("no new messages")