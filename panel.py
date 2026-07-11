from flask import Flask, request, redirect, render_template_string
import os

app = Flask(__name__)

VIDEO_FOLDER = "videos"

os.makedirs(VIDEO_FOLDER, exist_ok=True)


HTML = """
<!DOCTYPE html>
<html>
<head>
<title>IPTV Control Panel</title>

<meta name="viewport" content="width=device-width">

<style>

body{
    font-family: Arial;
    padding:20px;
    background:#111;
    color:white;
}

.box{
    background:#222;
    padding:15px;
    border-radius:10px;
    margin-bottom:10px;
}

button{
    padding:10px;
    border-radius:8px;
    border:0;
}

.delete{
    background:red;
    color:white;
}

.upload{
    background:green;
    color:white;
}

</style>

</head>

<body>


<h2>IPTV Control Panel</h2>


<div class="box">

<form action="/upload" method="post" enctype="multipart/form-data">

<input 
type="file"
name="file"
accept="video/*"
required
>

<br><br>

<button class="upload">
Upload Video
</button>

</form>

</div>



<h3>Videos</h3>


{% for video in videos %}

<div class="box">

{{video}}

<br><br>

<a href="/delete/{{video}}">

<button class="delete">
Delete
</button>

</a>

</div>

{% else %}

<p>No videos</p>

{% endfor %}


</body>
</html>
"""



def get_videos():

    return sorted([
        f for f in os.listdir(VIDEO_FOLDER)
        if f.lower().endswith(
            (
                ".mp4",
                ".mkv",
                ".avi"
            )
        )
    ])



@app.route("/")
def home():

    return render_template_string(
        HTML,
        videos=get_videos()
    )



@app.route("/upload", methods=["POST"])
def upload():

    if "file" not in request.files:
        return "No file"


    file = request.files["file"]


    if file.filename == "":
        return "No filename"


    if not file.filename.lower().endswith(
        (
            ".mp4",
            ".mkv",
            ".avi"
        )
    ):
        return "Only video allowed"


    path = os.path.join(
        VIDEO_FOLDER,
        file.filename
    )


    file.save(path)


    return redirect("/")



@app.route("/delete/<name>")
def delete(name):

    path = os.path.join(
        VIDEO_FOLDER,
        name
    )


    if os.path.exists(path):

        os.remove(path)


    return redirect("/")



if __name__ == "__main__":

    app.run(
        host="0.0.0.0",
        port=5000
    )