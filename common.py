import os.path
import pickle
import threading
import time

import vlc

from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow


ALLOWED = 1
VIDEO_ENDED = 6
TOKEN_FILE = 'token.pickle'
CREDS_FILE = 'credentials.json'
SCOPES = [
    'https://www.googleapis.com/auth/calendar.readonly', 
    "https://www.googleapis.com/auth/youtube.readonly",
]

settings_lock = threading.Lock()
settings = {
    'morning_start_time': 5, 
    'morning_end_time': 14, 
    'wakeup_time_hour': 7, 
    'wakeup_time_min': 0, 
    'wakeup_time_from_calendar': True, 
    'alarm_minutes_before_event': 60,
}


def get_creds() -> Credentials:
    creds = None
    if os.path.exists(TOKEN_FILE):
        with open(TOKEN_FILE, 'rb') as token:
            creds = pickle.load(token)
    
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                CREDS_FILE, SCOPES)
            creds = flow.run_local_server(port=0)
        
        with open(TOKEN_FILE, 'wb') as token:
            pickle.dump(creds, token)
    

    return creds


def play_video(video):
    p = vlc.MediaPlayer(video)
    p.set_fullscreen(ALLOWED)
    p.play()
    while p.get_state() != VIDEO_ENDED:
        time.sleep(1)
    p.stop()

