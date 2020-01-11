import re
import socket
import time
from typing import Dict

import vlc

from googleapiclient.discovery import build

import common

try:
    import pafy
except ImportError:
    Output.install_youtube_dl()


class Output:
    @staticmethod
    def web_driver_exception():
        print('You need to install gecodriver from here https:'
            'http://github.com/mozilla/geckodriver/releases'
            '\nMake sure your Firefox and gecodriver is in PATH, then try '
            'again.')

    @staticmethod     
    def install_youtube_dl():
        print("You need to install youtube-dl with 'sudo pip install --upgrade youtube_dl'")


class YouTube():
    PLAYLIST_NAME = 'superalarmclock'
    BASE_URL = 'https://www.youtube.com/watch?v='
    PLAYLIST_INDEX_FILE = 'song_in_playlist.txt'
    REPLACE_PATTERN = r'[_\-\s]'


    def __init__(self, creds):
        self.account = build('youtube', 'v3', credentials=creds)
        self.playlist_id = self.get_alarm_playlist_id()
        with open(YouTube.PLAYLIST_INDEX_FILE) as playlist_index:
            self.song_in_playlist = int(playlist_index.read())
        
    def get_alarm_playlist_id(self):
        request = self.account.playlists().list(
            part="snippet,contentDetails",
            maxResults=25,
            mine=True
        )
        response = request.execute()
        for playlist in response['items']:
            if YouTube.get_playlist_name(playlist) == YouTube.PLAYLIST_NAME:
                return playlist['id']

    def get_next_song_url(self) -> str:
        request = self.account.playlistItems().list(
            part="snippet,contentDetails",
            maxResults=25,
            playlistId=self.playlist_id,
        )
        playlist = request.execute()
        self.song_in_playlist = (self.song_in_playlist + 1) % len(playlist['items'])
        with open(YouTube.PLAYLIST_INDEX_FILE, 'w') as playlist_index:
            playlist_index.write(str(self.song_in_playlist))

        return (
            YouTube.BASE_URL + playlist['items'][self.song_in_playlist]
            ['contentDetails']['videoId']
        )
    
    def play_next_song(self):
        video = pafy.new(self.get_next_song_url()).getbest().url
        common.play_video(video)


    @staticmethod
    def get_playlist_name(playlist: Dict) -> str:
        name = playlist['snippet']['title'].lower()
        name = re.sub(YouTube.REPLACE_PATTERN, '', name)
        return "".join(name)

