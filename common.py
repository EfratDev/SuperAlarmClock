import os.path
import pickle
import threading
import time

import vlc

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow

import snooze


ALLOWED = 1
VIDEO_ENDED = 6
SNOOZE = 0
KEEP_PLAYING = 1
TOKEN_FILE = 'token.pickle'
CREDS_FILE = 'credentials.json'
SCOPES = [
    'https://www.googleapis.com/auth/calendar.readonly', 
    "https://www.googleapis.com/auth/youtube.readonly",
]

settings_lock = threading.Lock()
settings = {
    'snooze_minutes': '10',
    'morning_start_time': '05:00',
    'morning_end_time': '14:00',
    'wakeup_time': '10:00',
    'wakeup_time_from_calendar': True,
    'alarm_minutes_before_event': '60',
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


def snooze_feature(func):
    def wrapper(*args, **kwargs):
        global SNOOZE
        SNOOZE = 0
        func(*args, **kwargs)
        while SNOOZE:
            time.sleep(int(settings['snooze_minutes']) * 60)
            func(*args, **kwargs)
    return wrapper


def play_video(video):
    global KEEP_PLAYING
    KEEP_PLAYING = 1
    p = vlc.MediaPlayer(video)
    p.set_fullscreen(ALLOWED)
    p.play()
    time.sleep(3)
    driver = snooze.popup_snooze()
    while p.get_state() != VIDEO_ENDED and KEEP_PLAYING:
        time.sleep(1)
    driver.close()
    p.stop()

