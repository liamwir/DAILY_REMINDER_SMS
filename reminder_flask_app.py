from __future__ import print_function

import datetime
import time
import os.path
import boto3
import json

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from flask import Flask
from markupsafe import escape

BUCKET = "zappa-reminder-flask-app"
CRED_FILE = "token.json"

SCOPES = ['https://www.googleapis.com/auth/calendar.readonly']
CALENDARS = {'Holidays in United States': 'en.usa#holiday@group.v.calendar.google.com',
'liamwir12@gmail.com': 'liamwir12@gmail.com',
'Jaguars Whisperer': 's7ouavn9ureqrmbi7pe7uhvlao@group.calendar.google.com',
'Birthdays': 'addressbook#contacts@group.v.calendar.google.com',
'White Mouse': 'te5753o0vfujoc264580j6egbo@group.calendar.google.com',
'Rosenstrasse Foundation': '4l3hbp5t754f24qsmq042h7ghc@group.calendar.google.com',
'LIS 5472 - SP 23 (Digital Libraries)': '3f75697c2b42d4d7b25eca485b2fa800ca3e0f5e936a919b474ab5de21636f7a@group.calendar.google.com',
'LIS 5524 - SP 23 (Instructional Role of the Information Professional)': '4f93ea0b30c7304927791a0d7babd20f20e4fc76c62ac1febde1a750a490e0bb@group.calendar.google.com',
'LIS 5566 - SP 23 (Diverse Resources for Children & YA)': '89c1edba19cfd49830eeeb82e32e43e96c46a0756629bba8cb47a5a25b23ba61@group.calendar.google.com',
'Volunteer: NEB': 'ifc1tt3hhut0eri8t51bq32ntk@group.calendar.google.com',
'Work: STEM Libraries GA': 'h2gh4teullsid40d5is24djitg@group.calendar.google.com',
'WM Spring 2023 Season': '1fa07adc82633bb01cfee9eac7c9b8d8f04f7eb7ce3bd1a039dbd91783bcab72@group.calendar.google.com',
'HCAMI Rehearsal Schedule - SP 23': '446518d3e8b2d1f78fb479116e33dcf968385f8c4925f3f7466773ace7a3d3f0@group.calendar.google.com'}

app = Flask(__name__)

s3 = boto3.client('s3')

#[Endpoints]------------------------------------------------------

@app.route('/credentials/refresh')
def credentials_refresh_endpoint():
   return credentials_refresh()

@app.route('/events/all')
def retrieve_events_endpoint():
    all_events = get_events_list()
    return f'Events = {all_events}'

#[Events]------------------------------------------------------

def credentials_refresh():
    creds = get_credentials()
    before = f"Before Refresh: expiry = {creds.expiry}"
    creds.refresh(Request())
    after = f"After Refresh: expiry = {creds.expiry}"
    save_credentials(creds)
    return f'{before}\n {after}'

def local_to_utc_iso(some_local_time):

    # convert to UTC
    utc_offset = datetime.datetime.utcnow() - datetime.datetime.now()

    # calculate the UTC time by subtracting the UTC offset from the local time
    utc_time = some_local_time + utc_offset

    # format in ISO format
    iso_format = '%Y-%m-%dT%H:%M:%S.%fZ'
    now_utc_iso = utc_time.strftime(iso_format)

    return now_utc_iso

def get_events_list():
    
    service = build('calendar', 'v3', credentials=get_credentials())
 
    now = local_to_utc_iso(datetime.datetime.now())
    start_of_day = local_to_utc_iso(datetime.datetime.combine(datetime.date.today(), datetime.datetime.min.time()))
    end_of_day = local_to_utc_iso(datetime.datetime.combine(datetime.date.today(), datetime.datetime.max.time()))
    print('Retrieving events from all intersting calendars...')

    events = []
    for calendar_name, calendar_id in CALENDARS.items():
        print(f"- retrieving events of calendar '{calendar_name}'") 
        events_result = service.events().list(
            calendarId=calendar_id,
            timeMin=now,
            timeMax=end_of_day,
            maxResults=100, 
            singleEvents=True,
            orderBy='startTime'
            ).execute()
        events = events + events_result.get('items', [])

    if not events:
        print('No upcoming events found.')

    all_events = ""

    for event in events:
        start = event['start'].get('dateTime', event['start'].get('date'))
        print(start, event['summary'])
        all_events = all_events + f"<br>{start}: {event['summary']}"
    
    return all_events

#[Credentials]------------------------------------------------------

def get_credentials():
    data = s3.get_object(Bucket=BUCKET, Key=CRED_FILE)
    data_json = data['Body'].read().decode('utf-8')

    return Credentials.from_authorized_user_info(json.loads(data_json), SCOPES)

    """
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
        return creds
    else:
        raise Exception('Token file does not exist') 
    """

def save_credentials(creds):
    s3.put_object(Body=creds.to_json(), Bucket=BUCKET, Key=CRED_FILE)

    
    """
    with open('token.json', 'w') as token:
        token.write(creds.to_json())
    """

