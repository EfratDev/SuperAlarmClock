from collections import namedtuple
from typing import NamedTuple, Optional
import datetime as dt
import logging
import socket
import time

from httplib2 import ServerNotFoundError
import google.auth.exceptions
import vlc

import common
import google_calendar_api as gc
import youtube_api


EVENT_REFRESH_INTERVAL = 5 * 60
CONNECTION_TRIES = 3
NO_INTERNET_VIDEO = "no_internet_song.mp4"


web_dependent_vars = namedtuple(
    'Conn',
    ['is_from_calendar','youtube_session','wakeup_time']
)
params = namedtuple(
    'Params',
    ['youtube_session', 'secondes_before_event', 'wakeup_time']
)


def get_video(youtube_session: youtube_api.YouTube) -> str:
    for _ in range(CONNECTION_TRIES):
        try:
            return youtube_session.get_next_song()
        except (AttributeError, socket.timeout) as e:
            logging.warning(e)
    return NO_INTERNET_VIDEO


@common.snooze_feature
def alarm(youtube_session: youtube_api.YouTube) -> None:
    common.play_video(get_video(youtube_session))


def wait_until_alarm(
        secondes_before_event: int,
        wakeup_time: Optional[dt.time]
        ) -> None:
    time_until_alarm = (wakeup_time - dt.datetime.now()).total_seconds()
    time_until_alarm -= secondes_before_event
    time.sleep(min(EVENT_REFRESH_INTERVAL, max(time_until_alarm, 0)))
    return time_until_alarm <= EVENT_REFRESH_INTERVAL  # alarm or refresh data


def _get_wakeup_date(
        is_from_calendar: bool, 
        wakeuptime: dt.time, 
        earliest_wakeup: dt.time
        ) -> dt.datetime:
    now_time = dt.datetime.now().time()
    if ((is_from_calendar and now_time > earliest_wakeup) or
            (not is_from_calendar and wakeuptime < now_time)):
        return dt.date.today() + dt.timedelta(days=1)
    return dt.datetime.today()


def get_user_input() -> list:
    with common.settings_lock:
        return list(common.settings.values())[1:]  # without snooze minutes


def convert_strtime_to_time(str_time: str) -> dt.time:
    return dt.datetime.strptime(str_time, "%H:%M").time()


def get_web_dependent_vars(
        is_from_calendar: bool, 
        earliest_wakeup: dt.time, 
        latest_wakeup: dt.time,
        ) -> NamedTuple:
    try:
        google_api_creds = common.get_creds()
        youtube_session = youtube_api.YouTube(google_api_creds)
        calendar_conn = gc.Calendar(
            google_api_creds, 
            earliest_wakeup, 
            latest_wakeup
        )
        wakeup_time = calendar_conn.get_first_event_datetime()
    except (ServerNotFoundError, google.auth.exceptions.TransportError):
        return web_dependent_vars(False, False, False)

    return web_dependent_vars(is_from_calendar, youtube_session, wakeup_time)


def initialize(
        earliest_wakeup: dt.time, 
        latest_wakeup: dt.time,
        wakeup_time: dt.time, 
        is_from_calendar: bool, 
        minutes_before_event: int,
    ) -> NamedTuple:
    earliest_wakeup = convert_strtime_to_time(earliest_wakeup)
    latest_wakeup = convert_strtime_to_time(latest_wakeup)
    wakeup_time = convert_strtime_to_time(wakeup_time)
    wakeup_date = _get_wakeup_date(
        is_from_calendar, 
        wakeup_time, 
        earliest_wakeup
    )
    wakeup_time = dt.datetime.combine(wakeup_date, wakeup_time)
    secondes_before_event = int(minutes_before_event) * 60
    conn = get_web_dependent_vars(
        is_from_calendar,
        earliest_wakeup, 
        latest_wakeup
    )

    if conn.is_from_calendar:
        if conn.wakeup_time is None:
            wakeup_time = dt.datetime.now() + dt.timedelta(days=999)
        else:
            wakeup_time = conn.wakeup_time
    else:
        secondes_before_event = 0
    
    return params(conn.youtube_session, secondes_before_event, wakeup_time)


def super_alarm_clock() -> None:
    while True:
        params = initialize(*get_user_input())
        if wait_until_alarm(params.secondes_before_event, params.wakeup_time):
            alarm(params.youtube_session)

super_alarm_clock()