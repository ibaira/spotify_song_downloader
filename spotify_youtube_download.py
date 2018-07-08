#!/usr/bin/env python
# -*- coding: utf-8 -*
from __future__ import unicode_literals
from bs4 import BeautifulSoup
import dbus
import logging
import os
import sys
import unicodedata
from urllib.request import urlopen
import urllib.parse
import youtube_dl


def create_logger():
    """Create a logger showing a timestamp and a message

    :rtype logging.Logger
    """
    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG)
    ch = logging.StreamHandler(sys.stdout)
    ch.setLevel(logging.DEBUG)
    formatter = logging.Formatter('[%(asctime)s] %(message)s')
    ch.setFormatter(formatter)
    logger.addHandler(ch)
    return logger


def rm_accents(input_str):
    """Remove accents and special characters"""
    nfkd_form = unicodedata.normalize('NFKD', input_str)
    return "".join([c for c in nfkd_form if not unicodedata.combining(c)])


def download_webfile(url, filename=None, **ydl_opts):
    """Download mp3 song from YouTube"""
    if filename is not None:
        ydl_opts = {
            'format': 'bestaudio/best',
            'outtmpl': filename, 
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192',
            }],
        }

        with youtube_dl.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])
        

def get_song_metadata():
    """Return the song title and artist from the song currently being played

    :rtype title (string), artist (string)
    """
    session_bus = dbus.SessionBus()
    spotify_bus = session_bus.get_object("org.mpris.MediaPlayer2.spotify",
                                         "/org/mpris/MediaPlayer2")
    spotify_properties = dbus.Interface(spotify_bus,
                                        "org.freedesktop.DBus.Properties")
    # Get metadata dict
    metadata = spotify_properties.Get("org.mpris.MediaPlayer2.Player",
                                      "Metadata")
    return metadata['xesam:title'], metadata['xesam:albumArtist'][0]


def get_video_entries():
    """Search video URLs in YouTube and extract information

    :rtype Soup object including the parsed result entries
    """
    query = urllib.parse.quote(textToSearch)
    url = "https://www.youtube.com/results?search_query=" + query
    response = urlopen(url)
    html = response.read()
    soup = BeautifulSoup(html, "lxml")
    return soup


def config_dst_folder(s_title, s_artist, folder="Music"):
    """Set destination song path"""
    return '{0}/{dir}/{1} - {2}'.format(os.environ['HOME'],
                                        rm_accents(s_title),
                                        rm_accents(s_artist),
                                        dir=folder)


if __name__ == '__main__':
    log = create_logger()
    # Read current song in Spotify and obtain its name and artist
    title, artist = get_song_metadata()
    log.info(title + " - " + artist)

    # Prepare Search keywords removing special characters
    textToSearch = rm_accents(title) + rm_accents(artist) + " Official Music Video"
    # Search on YouTube and get url of the video
    youtube_entries = get_video_entries()

    # Get just the first (limit=1) entry of the YouTube page
    tmp_filename = './new_song'
    # Parse html entry into dict to get href
    for vid in youtube_entries.findAll(attrs={'class': 'yt-uix-tile-link'}, limit=1):
        log.info('https://www.youtube.com' + vid['href'])
        # Download audio from YouTube using youtube-dl
        download_webfile('https://www.youtube.com' + vid['href'], tmp_filename)

    # Move .mp3 file to the right directory and with a proper name
    destination = config_dst_folder(title, artist)
    log.info("The song will be saved in: " + destination + ".mp3\n")
    for f in os.listdir("."):
        if f == ".mp3":
            os.rename(f, destination)
