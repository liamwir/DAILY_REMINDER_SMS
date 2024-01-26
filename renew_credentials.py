from __future__ import print_function

import os.path
import boto3
import json

from google_auth_oauthlib.flow import InstalledAppFlow

# If modifying these scopes, delete the file token.json.
SCOPES = ['https://www.googleapis.com/auth/calendar.readonly']

CRED_FILE_PATH= os.path.join(os.path.dirname(os.path.realpath(__file__)), "credentials.json")
TOKEN_FILE_PATH= os.path.join(os.path.dirname(os.path.realpath(__file__)), "token.json")
BUCKET = "zappa-reminder-flask-app"
CRED_FILE = "token.json"

s3 = boto3.client('s3')
                             
def get_credentials():
    """
    Ask the user to login and save the credentials to the token.json file in the directory.
    The file token.json stores the user's access and refresh tokens.
    """
    print("Getting credentials from user...")

    flow = InstalledAppFlow.from_client_secrets_file(CRED_FILE_PATH, SCOPES)
    creds = flow.run_local_server(port=0)
    return creds

def save_credendtials_to_file(creds):
    """ Save the credentials to a local file """
   
    print("Saving credentials to local file...")

    with open(TOKEN_FILE_PATH, 'w+') as token:
        token.write(creds.to_json())

def save_credendtials_to_s3(creds):
    """ Save the credentials to s3 """
    
    print("Saving credentials to s3...")
    s3.put_object(Body=creds.to_json(), Bucket=BUCKET, Key=CRED_FILE)


if __name__ == '__main__':
    creds = get_credentials()
    save_credendtials_to_file(creds)
    save_credendtials_to_s3(creds)