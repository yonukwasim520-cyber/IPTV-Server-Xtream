from flask import Flask, Response, jsonify, request, render_template_string, redirect

import os
import socket
import subprocess
import threading
import queue
from collections import deque
import time
import copy




app = Flask(__name__)



USERNAME = "test"
PASSWORD = "1234"


VIDEO_FOLDER = "videos"


streams = {}

timeshift_buffer = {}

rewind_request = {}

current_process = None
current_channel = None


playlist_version = 1






def get_ip():

    s = socket.socket(
        socket.AF_INET,
        socket.SOCK_DGRAM
    )

    try:

        s.connect(
            ("8.8.8.8", 80)
        )

        return s.getsockname()[0]


    finally:

        s.close()






def get_videos():

    os.makedirs(
        VIDEO_FOLDER,
        exist_ok=True
    )


    return sorted([

        f for f in os.listdir(VIDEO_FOLDER)

        if f.lower().endswith(".mp4")

    ])
    # =========================
# XTREAM IPTV API
# =========================


@app.route("/player_api.php")
def player_api():


    user = request.args.get("username")

    password = request.args.get("password")

    action = request.args.get("action")



    print("PLAYER API REQUEST:")

    print(request.args)





    if user != USERNAME or password != PASSWORD:


        return jsonify({

            "user_info":{

                "auth":0

            }

        })







    if action is None:


        return jsonify({


            "user_info":{


                "username":USERNAME,

                "password":PASSWORD,

                "message":"Welcome",

                "auth":1,

                "status":"Active",

                "exp_date":"1893456000",

                "is_trial":"0",

                "active_cons":"0",

                "created_at":"1893456000",

                "max_connections":"1",

                "allowed_output_formats":[

                    "ts"

                ]

            },



            "server_info":{


                "url":get_ip(),

                "port":"8080",

                "server_protocol":"http",

                "https_port":"0",

                "rtmp_port":"0",

                "timezone":"UTC"

            }


        })









    if action == "get_live_categories":


        return jsonify([

            {

                "category_id":"1",

                "category_name":"Videos"

            }

        ])








    if action == "get_live_streams":


        result = []



        for i,v in enumerate(get_videos(),1):


            result.append({


                "num":i,


                "name":

                os.path.splitext(v)[0],


                "stream_type":"live",


                "stream_id":i,


                "category_id":"1",


                "container_extension":"ts",


                "direct_source":

                f"http://{get_ip()}:8080/live/{USERNAME}/{PASSWORD}/{i}.ts"


            })



        return jsonify(result)







    return jsonify([])
    # =========================
# FILE SYSTEM
# =========================


@app.route("/upload", methods=["POST"])
def upload():


    global playlist_version



    if "file" not in request.files:


        return jsonify({

            "status":"error",

            "message":"No file"

        })



    file = request.files["file"]



    if not file.filename.lower().endswith(".mp4"):


        return jsonify({

            "status":"error",

            "message":"Only MP4 allowed"

        })




    os.makedirs(

        VIDEO_FOLDER,

        exist_ok=True

    )



    path = os.path.join(

        VIDEO_FOLDER,

        file.filename

    )



    file.save(path)



    playlist_version += 1



    return redirect("/")







@app.route("/files")
def files():


    return jsonify(

        get_videos()

    )







@app.route("/delete/<name>")
def delete(name):


    global playlist_version



    path = os.path.join(

        VIDEO_FOLDER,

        name

    )



    if os.path.exists(path):


        os.remove(path)



        playlist_version += 1



        return redirect("/")



    return jsonify({

        "status":"missing"

    })








# =========================
# WEB PANEL
# =========================


@app.route("/")
def panel():


    html = """

<!DOCTYPE html>

<html>

<head>

<title>IPTV Control</title>


<meta name="viewport" content="width=device-width">


</head>


<body>


<h2>IPTV Server Control</h2>



<form action="/upload" method="post" enctype="multipart/form-data">


<input type="file" name="file" accept=".mp4">


<button type="submit">

Upload

</button>


</form>



<hr>



<h3>Videos</h3>



{% for v in videos %}


<p>

{{v}}

<a href="/delete/{{v}}">

Delete

</a>


</p>



{% endfor %}



<h4>

Playlist Version: {{version}}

</h4>



</body>

</html>

"""


    return render_template_string(

        html,

        videos=get_videos(),

        version=playlist_version

    )
    # =========================
# VIDEO STREAM
# =========================



def create_stream(channel):

    global current_process
    global current_channel


    if current_channel == channel and channel in streams:

        return streams[channel]


    if current_process:

        try:

            current_process.terminate()

        except:

            pass


    streams.clear()

    time.sleep(0.2)


    videos = get_videos()


    if channel < 1 or channel > len(videos):

        return None


    video = os.path.join(

        VIDEO_FOLDER,

        videos[channel-1]

    )


    q = queue.Queue(

        maxsize=1800

    )


    timeshift_buffer[channel] = deque(
        maxlen=50
    )

    def run():

        global current_process


        cmd = [

            "ffmpeg",

            "-re",

            "-stream_loop",

            "-1",

            "-i",

            video,

            "-c:v",

            "copy",

            "-c:a",

            "aac",

            "-f",

            "mpegts",

            "-mpegts_flags",

            "+resend_headers",

            "pipe:1"

        ]


        current_process = subprocess.Popen(

            cmd,

            stdout=subprocess.PIPE,

            stderr=subprocess.DEVNULL

        )


        while True:

            if current_process.poll() is not None:

                break


            data = current_process.stdout.read(

                188*100

            )


            if data:
                q.put(data)



    threading.Thread(

        target=run,

        daemon=True

    ).start()


    streams[channel] = q

    current_channel = channel


    return q







@app.route("/live/<user>/<password>/<int:id>.ts")
def live(user,password,id):

    if user != USERNAME or password != PASSWORD:

        return "Denied",403


    q = create_stream(id)


    if q is None:

        return "Missing",404


    def gen():

        while True:

            data = q.get()

            timeshift_buffer[id].append(data)

            yield data


    return Response(

        gen(),

        mimetype="video/mp2t"

    )
    
     
    
    
    
    # =========================
# START SERVER
# =========================


def run_iptv():


    app.run(

        host="0.0.0.0",

        port=8080,

        threaded=True

    )





if __name__ == "__main__":


    os.makedirs(

        VIDEO_FOLDER,

        exist_ok=True

    )



    print("======================")

    print("IPTV SERVER STARTED")

    print("======================")


    print(

        "IPTV : http://" +

        get_ip() +

        ":8080"

    )


    print(

        "PANEL: http://" +

        get_ip() +

        ":5000"

    )





    threading.Thread(

        target=run_iptv,

        daemon=True

    ).start()



    # لوحة التحكم

    app.run(

        host="0.0.0.0",

        port=5000,

        threaded=True

    )