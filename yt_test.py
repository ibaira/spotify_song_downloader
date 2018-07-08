#!/usr/bin/env python
# -*- coding: utf-8 -*

"""Script to detect and download the song which is currently being played on
Spotify.

It is tested on Windows and Ubuntu platforms.
"""

from __future__ import unicode_literals
from bs4 import BeautifulSoup
import os
import platform
import re
import unicodedata
import urllib
import urllib2
import youtube_dl
import sys

import win32gui
import win32con
import win32clipboard


def remove_accents(input_str):
    nfkd_form = unicodedata.normalize('NFKD', input_str)
    return "".join([c for c in nfkd_form if not unicodedata.combining(c)])


def download_web_file(url, filename=None, **ydl_opts):
    if filename is not None:
        ydl_opts = {
            'format': 'bestaudio/best',
            'outtmpl': unicode(filename),
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192',
            }],
        }

        with youtube_dl.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])


def download_web_file_win(url, filename=None, **ydl_opts):
    if filename is not None:
        ydl_opts = dict(
            format='bestaudio/best',
            outtmpl='%(title)s-%(id)s.%(ext)s',
            postprocessors=[
                dict(
                    key='FFmpegExtractAudio',
                    preferredcodec='mp3')
            ]
        )

        with youtube_dl.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])


def enum_handler(hwnd, results):
    results[hwnd] = {
        "title": win32gui.GetWindowText(hwnd),
        "visible": win32gui.IsWindowVisible(hwnd),
        "minimized": win32gui.IsIconic(hwnd),
        "rectangle": win32gui.GetWindowRect(hwnd),  # (left, top, right, bottom)
        "next": win32gui.GetWindow(hwnd, win32con.GW_HWNDNEXT)  # Window handle to below window
    }


def get_windows():
    enumerated_windows = {}
    win32gui.EnumWindows(enum_handler, enumerated_windows)
    return enumerated_windows


def main():
    """Linux main function"""
    # Read current song in Spotify and obtain its name and artist
    
    hwnd = win32gui.GetForegroundWindow()
    print str(hwnd)

    # session_bus = dbus.SessionBus()
    # spotify_bus = session_bus.get_object(
    #     "org.mpris.MediaPlayer2.spotify",
    #     "/org/mpris/MediaPlayer2"
    # )
    # spotify_properties = dbus.Interface(
    #     spotify_bus,
    #     "org.freedesktop.DBus.Properties"
    # )
    # metadata = spotify_properties.Get(
    #     "org.mpris.MediaPlayer2.Player",
    #     "Metadata"
    # )
    # # for key, value in metadata.items():
    # #     print key, value

    # # To just print the title and artist
    # print metadata['xesam:title']
    # print metadata['xesam:albumArtist'][0]

    # # Prepare Search key removing special characters
    # textToSearch = remove_accents(metadata['xesam:title']) + " " \
    #     + remove_accents(metadata['xesam:albumArtist'][0]) + " " \
    #     + "Official Music Video"

    # # Search on YouTube and give url of the video
    # query = urllib.quote(textToSearch)
    # url = "https://www.youtube.com/results?search_query=" + query
    # response = urllib2.urlopen(url)
    # html = response.read()
    # soup = BeautifulSoup(html, "lxml")

    # # Get just the first (limit=1) entry of the YouTube page
    # for vid in soup.findAll(attrs={'class': 'yt-uix-tile-link'}, limit=1):
    #     print 'https://www.youtube.com' + vid['href']

    #     # Download audio from YouTube using youtube-dl
    #     filename = './new_song'
    #     download_web_file('https://www.youtube.com' + vid['href'], filename)

    # # Move .mp3 file to the right directory and with a proper name
    # destination = '{0}/Music/{1}-{2}'.format(
    #     os.environ['HOME'],
    #     remove_accents(metadata['xesam:title']),
    #     remove_accents(metadata['xesam:albumArtist'][0])
    # )

    # print "The song will be saved in: ", destination, ".mp3\n"
    # for f in os.listdir("."):
    #     if f == ".mp3":
    #         os.rename(f, destination)


def get_window_text(hwnd):
    buf_size = 1 + win32gui.SendMessage(hwnd, win32con.WM_GETTEXTLENGTH, 0, 0)
    buf = win32gui.PyMakeBuffer(buf_size)
    win32gui.SendMessage(hwnd, win32con.WM_GETTEXT, buf_size, buf)
    return str(buf)


def main_win():
    """Windows main function"""
    # Get song name and artist
    windows = get_windows()

    for window_handle in windows:
        if "YouTube" in windows[window_handle]["title"]:
            # print "{}, {}, {}, {}".format(
            #     windows[window_handle]["minimized"],
            #     windows[window_handle]["rectangle"],
            #     windows[window_handle]["next"],
            #     windows[window_handle]["title"])
            # print remove_accents(
            #     unicode(windows[window_handle]))
            title = windows[window_handle]["title"]
            song = title.split("-")[0]
            artist = title.split("-")[1]
            # print "Song: " + song
            # print "Artist: " + artist

    # Set destination folder
    destination = '{0}/Music/{1}-{2}'.format(
        os.path.expanduser("~"),
        unicode(song),
        unicode(artist))

    # Get clipboard data
    win32clipboard.OpenClipboard()
    data = win32clipboard.GetClipboardData()
    win32clipboard.CloseClipboard()

    # Download file
    download_web_file_win(data, destination)

    # Rename and relocate file to the /Music folder
    # print "Current directory: ", os.listdir(".")
    for f in os.listdir("."):
        if re.search(song, f, re.IGNORECASE):
            try:
                os.rename(f, destination + ".mp3")
                print "File downloaded to {}".format(destination + ".mp3")
            except Exception:
                print "Error renaming the file to <user>/Music/<song>-<artist \
                    >.mp3"
    else:
        try:
            newest_mp3 = max(glob.iglob('*.[Mm][Pp]3'), key=os.path.getctime)
            dest_dir = os.path.expanduser("~") + "/Music/"
            try:
                shutil.move(newest_mp3, dest_dir)
            except:
                print "File already exists"
        except:
            pass


if __name__ == '__main__':
    if platform.system() == "Windows":
        import glob
        import shutil
        import spotilib
        main_win()
    elif platform.system() == "Linux":
        import dbus
        main()
    else:
        print "Sorry, we don't currently have support for time" + \
            sys.platform, "OS"
        print "Fails may occur..."
        main()

# if __name__ == "__main__":
#     windows = get_windows()
#
#     for window_handle in windows:
#         if windows[window_handle]["title"] is not "":
#             if "YouTube" in windows[window_handle]["title"]:
#                 # print get_window_text(window_handle)
#                 print "{}, {}, {}, {}".format(windows[window_handle]["minimized"],
#                                               windows[window_handle]["rectangle"],
#                                               windows[window_handle]["next"],
#                                               windows[window_handle]["title"])
#
#                 hwnd = win32gui.GetForegroundWindow()
#                 print "Foreground window: " + str(hwnd)
#
#                 omnibox_hwnd = win32gui.FindWindowEx(hwnd, 0, 'Chrome_OmniboxView', None)
#                 print "Omnibox chrome:  " + str(omnibox_hwnd)
#                 # print dir(win32gui)
#                 print "Window text: " + get_window_text(hwnd)
# print windows[window_handle]

# print "/n/n/n Start real function:/n"
# main_win()

# 0, (-7, 0, 967, 791), 3867158, (17) Eminem - Untouchable (Audio) - YouTube - Google Chrome

# from time import sleep
# import uiautomation as automation
#
# if __name__ == '__main__':
#     sleep(3)
#     control = automation.GetFocusedControl()
#     controlList = []
#     while control:
#         controlList.insert(0, control)
#         control = control.GetParentControl()
#     if len(controlList) == 1:
#         control = controlList[0]
#     else:
#         control = controlList[1]
#     address_control = automation.FindControl(
#         control,
#         lambda c,
#         d: isinstance(c, automation.EditControl) and "Address and search bar" in c.Name)
#     print address_control.CurrentValue()
