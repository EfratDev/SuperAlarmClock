from httplib2 import ServerNotFoundError
import datetime as dt
import socket
import time

import vlc

import google.auth.exceptions

import common
import google_calendar_api as gc
import youtube_api


EVENT_REFRESH_INTERVAL = 5 * 60
CONNECTION_TRIES = 3
NO_INTERNET_VIDEO = "no_internet_song.mp4"


def alarm(youtube_session):
    for _ in range(CONNECTION_TRIES):
        try:
            youtube_session.play_next_song()
        except AttributeError:
            continue
        except socket.timeout:
            common.play_video(NO_INTERNET_VIDEO)
        
        return True

    common.play_video(NO_INTERNET_VIDEO)


def alarm_from_calendar(
        user_input, 
        youtube_session, 
        morning_start_time, 
        morning_end_time, 
        alarm_sec_before_event, 
        wakeup_datetime,
        calendar, 
        ):
    while True:
        if get_user_input() != user_input:
            return
        if calendar:
            try:
                wakeup_datetime = calendar.get_first_event_datetime()
            except ServerNotFoundError:
                pass

            if wakeup_datetime is None:
                time.sleep(EVENT_REFRESH_INTERVAL)
                continue

        time_until_alarm = (wakeup_datetime - dt.datetime.now()).total_seconds()
        time_until_alarm -=  alarm_sec_before_event
        if time_until_alarm > EVENT_REFRESH_INTERVAL:
            time.sleep(EVENT_REFRESH_INTERVAL)
        elif time_until_alarm < 0:  # only for testing
            alarm(youtube_session)
            return
        else:
            time.sleep(time_until_alarm)
            alarm(youtube_session)
            return


def _get_alarm_date(morning_start_time):
        if dt.datetime.now().time() > morning_start_time:
            # return dt.date.today() + dt.timedelta(days=1)
            pass
        return dt.date.today()


def get_user_input():
    with common.settings_lock:
        return list(common.settings.values())


def initialize(
        morning_start_time, 
        morning_end_time, 
        wakeup_time_hour, 
        wakeup_time_sec,  
        wakeup_time_from_calendar, 
        alarm_minutes_before_event,
    ):
    morning_start_time = dt.time(morning_start_time)
    morning_end_time = dt.time(morning_end_time)
    wakeup_time = dt.time(wakeup_time_hour, wakeup_time_sec)
    alarm_date = _get_alarm_date(morning_start_time)
    wakeup_datetime = dt.datetime.combine(alarm_date, wakeup_time)
    alarm_sec_before_event = alarm_minutes_before_event * 60
    if not wakeup_time_from_calendar:
        calendar = False
        alarm_sec_before_event = 0
    
    try:
        google_api_creds = common.get_creds()
        youtube_session = youtube_api.YouTube(google_api_creds)
        calendar = gc.Calendar(
            google_api_creds, 
            morning_start_time, 
            morning_end_time
        )
    except (ServerNotFoundError, google.auth.exceptions.TransportError):
        wakeup_time_from_calendar = False
        youtube_session = None
        calendar = None
    
    return (
        morning_start_time, 
        morning_end_time, 
        wakeup_datetime, 
        alarm_sec_before_event, 
        youtube_session, 
        calendar,
    )


def super_alarm_clock():
    while True:
        user_input = get_user_input()
        (
            morning_start_time, 
            morning_end_time, 
            wakeup_datetime, 
            alarm_sec_before_event, 
            youtube_session, 
            calendar,
        ) = initialize(*user_input)
    
        alarm_from_calendar(
            user_input, 
            youtube_session, 
            morning_start_time, 
            morning_end_time, 
            alarm_sec_before_event, 
            wakeup_datetime, 
            calendar,
        )
