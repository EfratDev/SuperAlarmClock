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


@common.snooze_feature
def alarm(youtube_session):
    video = NO_INTERNET_VIDEO
    for _ in range(CONNECTION_TRIES):
        if video == NO_INTERNET_VIDEO:
            try:
                video = youtube_session.get_next_song()
            except (AttributeError, socket.timeout):
                continue

    common.play_video(video)
    return True


def wait_until_alarm(
        youtube_session, 
        morning_start_time, 
        morning_end_time, 
        alarm_sec_before_event, 
        wakeup_datetime,
        calendar, 
        ):
    if calendar:
        try:
            wakeup_datetime = calendar.get_first_event_datetime()
        except ServerNotFoundError:
            time.sleep(EVENT_REFRESH_INTERVAL)
            return

    time_until_alarm = (wakeup_datetime - dt.datetime.now()).total_seconds()
    time_until_alarm -=  alarm_sec_before_event
    if time_until_alarm > EVENT_REFRESH_INTERVAL:
        time.sleep(EVENT_REFRESH_INTERVAL)
    elif time_until_alarm < 0:
        alarm(youtube_session)
    else:
        time.sleep(time_until_alarm)
        alarm(youtube_session)


def _get_alarm_date(from_calendar, wakeuptime, morning_start_time):
    now_time = dt.datetime.now().time()
    if ((from_calendar and now_time > morning_start_time) or
            (not from_calendar and wakeuptime < now_time)):
        return dt.date.today() + dt.timedelta(days=1)
    
    return dt.datetime.today()


def get_user_input():
    with common.settings_lock:
        return list(common.settings.values())[1:]  # without snooze minutes


def convert_strtime_to_time(str_time):
    return dt.datetime.strptime(str_time, "%H:%M").time()


def get_web_dependent_vars(
        wakeup_time_from_calendar, 
        morning_start_time, 
        morning_end_time,
        ):
    try:
        google_api_creds = common.get_creds()
        youtube_session = youtube_api.YouTube(google_api_creds)
        calendar = gc.Calendar(
            google_api_creds, 
            morning_start_time, 
            morning_end_time
        )
    except (ServerNotFoundError, google.auth.exceptions.TransportError):
        return False, None, False

    return wakeup_time_from_calendar, youtube_session, calendar


def initialize(
        morning_start_time, 
        morning_end_time, 
        wakeup_time, 
        from_calendar, 
        alarm_minutes_before_event,
    ):
    morning_start_time = convert_strtime_to_time(morning_start_time)
    morning_end_time = convert_strtime_to_time(morning_end_time)
    wakeup_time = convert_strtime_to_time(wakeup_time)
    alarm_date = _get_alarm_date(from_calendar, wakeup_time, morning_start_time)
    wakeup_datetime = dt.datetime.combine(alarm_date, wakeup_time)
    alarm_sec_before_event = int(alarm_minutes_before_event) * 60
    from_calendar, youtube_session, calendar = get_web_dependent_vars(
        from_calendar,
        morning_start_time, 
        morning_end_time
    )
    if not from_calendar:
        calendar = False
        alarm_sec_before_event = 0
    
    return (
        youtube_session, 
        morning_start_time, 
        morning_end_time, 
        alarm_sec_before_event, 
        wakeup_datetime, 
        calendar,
    )


def super_alarm_clock():
    while True:
        wait_until_alarm(*initialize(*get_user_input()))
