from flask import Flask, Response, jsonify, request

import os
import socket
import subprocess
import threading
import time
import queue


app = Flask(__name__)


# =========================
# CONFIG
# =========================

USERNAME = "test"
PASSWORD = "1234"

VIDEO_FOLDER = "videos"

HOST = "0.0.0.0"

PORT = 8080



# =========================
# GLOBAL DATA
# =========================

streams = {}

processes = {}



# =========================
# GET LOCAL IP
# =========================

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


    except:

        return "127.0.0.1"


    finally:

        s.close()



# =========================
# GET VIDEOS
# =========================

def get_videos():

    os.makedirs(
        VIDEO_FOLDER,
        exist_ok=True
    )


    return sorted([

        f

        for f in os.listdir(VIDEO_FOLDER)

        if f.lower().endswith(".mp4")

    ])




# =====================
# XTREAM API
# =====================

@app.route("/player_api.php")
def player_api():

    username = request.args.get("username")
    password = request.args.get("password")
    action = request.args.get("action")


    if username != USERNAME or password != PASSWORD:

        return jsonify({
            "user_info": {
                "auth": 0
            }
        })


    if action is None:

        return jsonify({

            "user_info": {

                "username": USERNAME,
                "password": PASSWORD,
                "auth": 1,
                "status": "Active",
                "exp_date": "1893456000",
                "is_trial": "0",
                "active_cons": "0",
                "max_connections": "1",
                "allowed_output_formats": [
                    "ts"
                ]

            },

            "server_info": {

                "url": request.host.split(":")[0],
                "port": str(PORT),
                "server_protocol": "http",
                "timezone": "UTC"

            }

        })


    if action == "get_live_categories":

        return jsonify([

            {
                "category_id": "1",
                "category_name": "Videos",
                "parent_id": 0
            }

        ])



    if action == "get_live_streams":

        result = []

        for i, video in enumerate(get_videos(), 1):

            result.append({

                "num": i,

                "name": os.path.splitext(video)[0],

                "stream_id": i,

                "stream_type": "live",

                "container_extension": "ts",

                "category_id": "1",

                "direct_source":
                f"http://{request.host.split(':')[0]}:{PORT}/live/{USERNAME}/{PASSWORD}/{i}.ts"

            })


        return jsonify(result)



    return jsonify([])






# =====================
# Stream
# =====================


def create_stream(channel):


    if channel in streams:

        return streams[channel]



    videos=get_videos()


    if channel < 1 or channel > len(videos):

        return None



    video=os.path.join(
        VIDEO_FOLDER,
        videos[channel-1]
    )



    q=queue.Queue(
        maxsize=1800
    )



    def run():

        process=subprocess.Popen(

            [

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

            ],

            stdout=subprocess.PIPE,

            stderr=subprocess.DEVNULL

        )



        processes[channel]=process



        while True:

            data=process.stdout.read(
                188*100
            )


            if not data:
                break


            q.put(data)



    threading.Thread(
        target=run,
        daemon=True
    ).start()



    streams[channel]=q


    return q






@app.route("/live/<user>/<password>/<int:id>.ts")
def live(user,password,id):


    if user != USERNAME or password != PASSWORD:

        return "Denied",403



    q=create_stream(id)


    if q is None:

        return "Missing",404



    def gen():

        while True:

            yield q.get()



    return Response(

        gen(),

        mimetype="video/mp2t"

    )






# =====================
# PANEL
# =====================


@app.route("/",methods=["GET"])
def panel():

    html="""

<html>

<head>

<title>IPTV Panel</title>

<meta name="viewport" content="width=device-width">

</head>


<body>


<h2>IPTV Control Panel</h2>


<h3>videos Video</h3>


<form method="post" action="/upload" enctype="multipart/form-data">

<input type="file" name="file">


<button>

Upload

</button>

</form>



<hr>


<h3>Update</h3>


{% for v in videos %}


<p>

{{v}}


<a href="/delete/{{v}}">

<button>

Delete

</button>

</a>


</p>


{% endfor %}



</body>

</html>

"""


    return render_template_string(

        html,

        videos=get_videos()

    )







@app.route("/upload", methods=["POST"])
def upload():

    if "file" not in request.files:
        return jsonify({
            "status": "error",
            "message": "No file"
        }), 400


    file = request.files["file"]


    if file.filename == "":
        return jsonify({
            "status": "error",
            "message": "No filename"
        }), 400


    update_folder = "Update"


    os.makedirs(
        update_folder,
        exist_ok=True
    )


    save_path = os.path.join(
        update_folder,
        file.filename
    )


    try:

        file.save(save_path)


        return jsonify({

            "status": "success",

            "message": "File uploaded",

            "filename": file.filename

        })


    except Exception as e:

        return jsonify({

            "status": "error",

            "message": str(e)

        }), 500








@app.route("/delete/<name>")
def delete(name):


    path=os.path.join(
        VIDEO_FOLDER,
        name
    )


    if os.path.exists(path):

        os.remove(path)


    return redirect("/")






# =====================
# START
# =====================


def run_iptv():

    app.run(

        host="0.0.0.0",

        port=8080,

        threaded=True

    )





if __name__ == "__main__":

    import subprocess
    import socket


    def get_ip():
        s = socket.socket(
            socket.AF_INET,
            socket.SOCK_DGRAM
        )

        try:
            s.connect(("8.8.8.8", 80))
            return s.getsockname()[0]

        finally:
            s.close()



    os.makedirs(
        VIDEO_FOLDER,
        exist_ok=True
    )

    os.makedirs(
        "hls",
        exist_ok=True
    )


    ip = get_ip()


    print("======================")
    print("      IPTV SERVER")
    print("======================")

    print(
        "IPTV:"
        f" http://{ip}:8080"
    )

    print(
        "CONTROL PANEL:"
        f" http://{ip}:5000"
    )

    print("======================")


    # تشغيل لوحة التحكم تلقائياً
    subprocess.Popen(
        [
            "python",
            "panel.py"
        ]
    )


    # تشغيل IPTV
    app.run(
        host="0.0.0.0",
        port=8080,
        threaded=True
    )