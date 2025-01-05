# install this stuff first on local machine: pip install google-auth google-auth-oauthlib google-auth-httplib2 google-api-python-client requests
import datetime
import os
import pickle
import requests
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

# If modifying these SCOPES, delete the file token.pickle.
SCOPES = ['https://www.googleapis.com/auth/calendar.readonly']

def authenticate_google_calendar():
    creds = None
    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            creds = pickle.load(token)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)

    service = build('calendar', 'v3', credentials=creds)
    return service

def get_upcoming_events(service, time_min):
    events_result = service.events().list(calendarId='primary', timeMin=time_min,
                                          maxResults=10, singleEvents=True,
                                          orderBy='startTime').execute()
    return events_result.get('items', [])

def search_flights(start_location, destination, date, max_price, api_key):
    url = "https://partners.api.skyscanner.net/apiservices/browsequotes/v1.0/US/USD/en-US/{}/{}/{}"
    formatted_url = url.format(start_location, destination, date)
    headers = {
        'x-api-key': api_key
    }
    response = requests.get(formatted_url, headers=headers)
    return response.json() #only works if api returns json data
def main():
    calendar_service = authenticate_google_calendar()
    
    start_location = "SFO-sky"  
    destination = "LAX-sky"    
    date = "2025-01-10"          
    max_price = 300              
    api_key = "YOUR_SKYSCANNER_API_KEY" 

    time_min = datetime.datetime.utcnow().isoformat() + 'Z'  # 'Z' indicates UTC time
    events = get_upcoming_events(calendar_service, time_min)

    if not events:
        print("No upcoming events found. Searching for flights...")
        flights = search_flights(start_location, destination, date, max_price, api_key)
        print(flights) 
    else:
        print("User has upcoming events. Please check availability.")

if __name__ == '__main__':
    main()
