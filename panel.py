from flask import Flask, request, redirect, render_template_string, jsonify
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
accept="video/*"
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





<script>

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





function formatBytes(bytes){


    if(bytes === 0)
        return "0 B";


    let units =
    [
        "B",
        "KB",
        "MB",
        "GB"
    ];


    let index =
    Math.floor(
        Math.log(bytes) /
        Math.log(1024)
    );


    return (
        (bytes /
        Math.pow(1024,index))
        .toFixed(2)
        +
        " "
        +
        units[index]
    );

}


</script>



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


    os.makedirs(
        "Update",
        exist_ok=True
    )


    path = os.path.join(
        "videos",
        file.filename
    )


    file.save(path)


    return jsonify({
        "status": "success",
        "message": "Uploaded",
        "file": file.filename
    })



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