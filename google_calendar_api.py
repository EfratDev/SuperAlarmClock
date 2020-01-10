from datetime import datetime
import datetime as dt

from dateutil import parser, tz
import pytz

from googleapiclient.discovery import build

from common import get_creds


class Calendar:
    def __init__(
            self, 
            creds,  
            morning_start_time, 
            morning_end_time,
            ):
        self.calendar_account = build('calendar', 'v3', credentials=creds)
        self.morning_start_time = morning_start_time
        self.morning_end_time = morning_end_time
    
    def get_first_event_datetime(self):
        date = dt.date.today()
        self.utc_morning_start_time = self._to_utc(date, self.morning_start_time)
        self.utc_morning_end_time = self._to_utc(date, self.morning_end_time)
        event_utc_datetime = self._get_event_datetime()
        if event_utc_datetime is None:
            return None
        return (parser.parse(event_utc_datetime).astimezone(tz.tzlocal())
            .replace(tzinfo=None))

    def _to_utc(self, date, time):
        datetime_ = dt.datetime.combine(date, time)
        return (datetime_.astimezone(tz.tzutc()).replace(tzinfo=None)
            .isoformat() + 'Z')
        
    def _get_event_datetime(self):
        events_result = self.calendar_account.events().list(
            calendarId='primary', 
            timeMin=self.utc_morning_start_time, 
            timeMax=self.utc_morning_end_time, 
            maxResults=1, 
            singleEvents=True, 
            orderBy='startTime',
        ).execute()
        try:
            return events_result['items'][0]['start']['dateTime']
        except (IndexError, KeyError):
            return None