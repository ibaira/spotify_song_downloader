.PHONY: all dep build test clean
dep:
	pip install youtube-dl
	sudo apt-get install python3-dbus
	sudo apt-get install python3-bs4
	sudo apt-get install ffmpeg

run:
	python3 spotify_youtube_download.py
