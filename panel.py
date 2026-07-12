from flask import Flask, request, redirect, render_template_string, jsonify
import os

app = Flask(__name__)

VIDEO_FOLDER = "videos"

os.makedirs(VIDEO_FOLDER, exist_ok=True)


def clear_hls():

    import shutil


    if os.path.exists("hls"):

        for item in os.listdir("hls"):

            path = os.path.join(
                "hls",
                item
            )


            if os.path.isdir(path):

                shutil.rmtree(
                    path,
                    ignore_errors=True
                )

            else:

                try:

                    os.remove(path)

                except:

                    pass


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


.cancel{

    background:orange;
    color:white;

}


progress{

    width:100%;

}


</style>


</head>


<body>


<h2>IPTV Control Panel</h2>



<div class="box">


<h3>Upload Video</h3>


<input 
type="file"
id="file"
onchange="syncFiles()"
>


<br><br>


<button class="upload" onclick="uploadFile()">

Upload Video

</button>


<button class="cancel" onclick="cancelUpload()">

Cancel

</button>



<br><br>


<progress 
id="progress"
value="0"
max="100">
</progress>


<p id="status">

Waiting...

</p>



</div>





<h3>Videos</h3>



{% for video in videos %}

<div class="box">

<b>{{video}}</b>

<br><br>

<button
onclick="renameVideo('{{video}}')">

Rename

</button>

<a href="/delete/{{video}}">

<button class="delete">

Delete

</button>

</a>

</div>

{% else %}

<p>No videos</p>

{% endfor %}





<script>

function syncFiles(){

    document.getElementById("status").innerHTML =
    "Syncing files...";


    fetch("/sync")

    .then(response => response.json())

    .then(data => {

        document.getElementById("status").innerHTML =
        "Files synced: " + data.count;

    });

}

let xhr = null;
let startTime = 0;


function uploadFile(){

    let file =
    document.getElementById("file").files[0];

    if(!file){

        alert("Select video first");
        return;

    }

    let form =
    new FormData();

    form.append(
        "file",
        file
    );

    xhr = new XMLHttpRequest();

    startTime =
    new Date().getTime();

    xhr.open(
        "POST",
        "/upload",
        true
    );

    xhr.upload.onprogress = function(event){

        if(event.lengthComputable){

            let loaded =
            event.loaded;

            let total =
            event.total;

            let percent =
            (loaded / total) * 100;

            let currentTime =
            new Date().getTime();

            let elapsed =
            (currentTime - startTime) / 1000;

            let speed =
            loaded / elapsed;

            let timeLeft =
            (total - loaded) / speed;

            document.getElementById("progress").value =
            percent;

            document.getElementById("status").innerHTML =

            "Uploading: "
            + percent.toFixed(1)
            + "%<br>"
            + formatBytes(loaded)
            + " / "
            + formatBytes(total)
            + "<br>Speed: "
            + formatBytes(speed)
            + "/s"
            + "<br>Remaining: "
            + timeLeft.toFixed(0)
            + " sec";

        }

    };


    xhr.onload = function(){

        document.getElementById("status").innerHTML =
        "Upload finished";

        location.reload();

    };


    xhr.onerror = function(){

        document.getElementById("status").innerHTML =
        "Upload failed";

    };


    xhr.send(form);

}



function cancelUpload(){

    if(xhr){

        xhr.abort();

        document.getElementById("status").innerHTML =
        "Upload cancelled";

        document.getElementById("progress").value =
        0;

    }

}



function renameVideo(oldName){

    let newName = prompt(
        "Enter new filename",
        oldName
    );

    if(newName == null)
        return;

    if(newName.trim() == "")
        return;

    let form = new FormData();

    form.append(
        "old_name",
        oldName
    );

    form.append(
        "new_name",
        newName
    );

    fetch("/rename",{

        method:"POST",

        body:form

    })

    .then(r=>r.json())

    .then(data=>{

        alert(data.message);

        if(data.status=="success"){

            location.reload();

        }

    });

}



function formatBytes(bytes){

    if(bytes===0)
        return "0 B";

    let units=[
        "B",
        "KB",
        "MB",
        "GB"
    ];

    let index=Math.floor(
        Math.log(bytes)/
        Math.log(1024)
    );

    return (
        (bytes/
        Math.pow(1024,index))
        .toFixed(2)
        +" "
        +units[index]
    );

}

</script>



</body>

</html>
"""



def get_videos():

    os.makedirs(
        VIDEO_FOLDER,
        exist_ok=True
    )


    return sorted([

        f

        for f in os.listdir(VIDEO_FOLDER)

        if f.lower().endswith(
            (
                ".mp4",
                ".mkv",
                ".avi",
                ".mp3"
            )
        )

    ])
    
    
def clear_hls():

    import shutil


    if os.path.exists("hls"):

        shutil.rmtree(
            "hls",
            ignore_errors=True
        )


    os.makedirs(
        "hls",
        exist_ok=True
    )


    # Clear stream memory

    streams.clear()



    # Stop old ffmpeg

    for channel, process in list(processes.items()):

        try:

            process.terminate()

        except:

            pass


    processes.clear()


@app.route("/")
def home():

    return render_template_string(
        HTML,
        videos=get_videos()
    )



@app.route("/upload", methods=["POST"])
def upload():

    if "file" not in request.files:

        return jsonify({
            "status":"error",
            "message":"No file"
        }),400



    file = request.files["file"]


    if file.filename == "":

        return jsonify({
            "status":"error",
            "message":"No filename"
        }),400



    if not file.filename.lower().endswith(
        (
            ".mp4",
            ".mkv",
            ".avi",
            ".mp3"
        )
    ):

        return jsonify({
            "status":"error",
            "message":"Only media files allowed"
        }),400



    os.makedirs(
        VIDEO_FOLDER,
        exist_ok=True
    )


    save_path = os.path.join(
        VIDEO_FOLDER,
        file.filename
    )


    file.save(
        save_path
    )


    clear_hls()


    return jsonify({

        "status":"success",

        "message":"File uploaded",

        "filename":file.filename

    })



@app.route("/delete/<name>")
def delete(name):


    video_path = os.path.join(
        VIDEO_FOLDER,
        name
    )


    # Delete file

    if os.path.exists(video_path):

        os.remove(video_path)



    # Clear HLS + stop streams

    clear_hls()



    return redirect("/")


@app.route("/rename", methods=["POST"])
def rename():

    old_name = request.form.get("old_name")
    new_name = request.form.get("new_name")


    if not old_name or not new_name:

        return jsonify({

            "status": "error",

            "message": "Missing filename"

        })


    old_path = os.path.join(
        VIDEO_FOLDER,
        old_name
    )


    if not os.path.exists(old_path):

        return jsonify({

            "status": "error",

            "message": "File not found"

        })


    # Keep original extension if user did not type one
    old_ext = os.path.splitext(old_name)[1]

    if os.path.splitext(new_name)[1] == "":

        new_name += old_ext


    new_path = os.path.join(
        VIDEO_FOLDER,
        new_name
    )


    if os.path.exists(new_path):

        return jsonify({

            "status": "error",

            "message": "File already exists"

        })


    os.rename(
        old_path,
        new_path
    )


    # Clear old HLS cache
    clear_hls()


    # Clear old streams
    if "streams" in globals():

        streams.clear()


    # Stop old ffmpeg processes
    if "processes" in globals():

        for stream_id, process in list(processes.items()):

            try:

                process.terminate()

            except:

                pass

        processes.clear()


    return jsonify({

        "status": "success",

        "message": "Video renamed",

        "filename": new_name

    })
    

if __name__ == "__main__":

    app.run(
        host="0.0.0.0",
        port=5000
    )