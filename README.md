![Logo](logo.png)





IPTV Server Xtream

A simple IPTV server built with Python and Flask that works with Xtream Codes compatible players.

This project converts local MP4 video files into IPTV streams using the MPEG-TS format and provides an Xtream API interface.

Features

- ✅ Xtream Codes API support
- ✅ Automatic channel generation from MP4 files
- ✅ MPEG-TS (".ts") live streaming
- ✅ Web control panel
- ✅ Upload and delete and Renaming videos
- ✅ Works on Android (Termux) and Linux
- ✅ Lightweight and easy to run

---

Requirements

Before running the server, install:

- Python 3.10 or newer
- FFmpeg
- Flask

---

Installation

1. Clone the repository

git clone https://github.com/yonukwasim520-cyber/IPTV-Server-Xtream.git

Enter the project folder:

cd IPTV-Server-Xtream

---

2. Install Python dependencies

Install Flask:

pip install flask

---

3. Install FFmpeg

Termux (Android)

pkg install ffmpeg

Ubuntu / Linux

sudo apt install ffmpeg

---

Running the Server

Start the server:

python server.py

After startup, the server will display:

IPTV : http://YOUR-IP:8080
PANEL: http://YOUR-IP:5000

---

Adding Videos

Put your MP4 files inside:

videos/

Example:

videos/
 ├── channel1.mp4
 ├── movie.mp4
 └── live.mp4

Each video will automatically become an IPTV channel.

---

Control Panel

Open:

http://YOUR-IP:5000

The panel allows you to:

- Upload MP4 videos
- Delete videos
- View available channels

---

Xtream API Login

Default credentials:

Username:

test

Password:

1234

You can change them in:

config.py

Edit:

USERNAME = "test"
PASSWORD = "1234"

---

IPTV Player Setup

For Xtream Codes compatible players:

Server URL:

http://YOUR-IP:8080

Username:

test

Password:

1234

---

Notes

- This project is intended for personal use and testing.
- Only stream content that you have permission to use.
- Performance depends on your device and network speed.
- WiFi is recommended for local network streaming.

---

License

This project is open source and available for learning and personal projects.
