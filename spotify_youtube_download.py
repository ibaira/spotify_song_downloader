#!/usr/bin/env python
# -*- coding: utf-8 -*
from __future__ import unicode_literals
from bs4 import BeautifulSoup
import dbus
import os
import unicodedata
import urllib
import urllib2
import youtube_dl


def remove_accents(input_str):
    nfkd_form = unicodedata.normalize('NFKD', input_str)
    return "".join([c for c in nfkd_form if not unicodedata.combining(c)])

def download_webfile(url, filename=None, **ydl_opts):
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
        

if __name__ == '__main__':
    # Read current song in Spotify and obtain its name and artist
    session_bus = dbus.SessionBus()
    spotify_bus = session_bus.get_object("org.mpris.MediaPlayer2.spotify",
                                         "/org/mpris/MediaPlayer2")
    spotify_properties = dbus.Interface(spotify_bus,
                                        "org.freedesktop.DBus.Properties")
    metadata = spotify_properties.Get("org.mpris.MediaPlayer2.Player", 
                                      "Metadata")
    # for key, value in metadata.items():
    #     print key, value

    # To just print the title and artist
    print metadata['xesam:title']
    print metadata['xesam:albumArtist'][0]

    # Prepare Search key removing special characters
    textToSearch =   remove_accents(metadata['xesam:title']) + " " \
                   + remove_accents(metadata['xesam:albumArtist'][0]) + " " \
                   + "Official Music Video"  # keywords

    # Search on YouTube and give url of the video
    query = urllib.quote(textToSearch)
    url = "https://www.youtube.com/results?search_query=" + query
    response = urllib2.urlopen(url)
    html = response.read()
    soup = BeautifulSoup(html, "lxml")
    
    # Get just the first (limit=1) entry of the YouTube page 
    for vid in soup.findAll(attrs={'class':'yt-uix-tile-link'}, limit=1):
        print 'https://www.youtube.com' + vid['href']

    # Download audio from YouTube using youtube-dl
    filename = './new_song' 
    download_webfile('https://www.youtube.com' + vid['href'], filename)

    # Move .mp3 file to the right directory and with a proper name
    destination = '{0}/Music/{1}-{2}'.format(
                os.environ['HOME'],
                remove_accents(metadata['xesam:title']), 
                remove_accents(metadata['xesam:albumArtist'][0])
    )

    print "The song will be saved in: ", destination, ".mp3\n"
    for f in os.listdir("."):
        if f == ".mp3":
            os.rename(f, destination)
