from flask import Flask, render_template, Response, request, jsonify
from detector import EPIDetector

import cv2
import os

app = Flask(__name__)

UPLOAD_FOLDER = "static/uploads"

os.makedirs(UPLOAD_FOLDER, exist_ok=True)

app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

detector = EPIDetector()

camera = None

video_source = 0

@app.route("/")
def index():

    return render_template("index.html")

@app.route("/start_webcam")
def start_webcam():

    global camera
    global video_source

    video_source = 0

    if camera is not None:

        camera.release()

    camera = None

    return jsonify({

        "success": True

    })

@app.route("/upload_video", methods=["POST"])
def upload_video():

    global camera
    global video_source

    if "video" not in request.files:

        return jsonify({

            "success": False,

            "message": "Vídeo não enviado."

        })

    file = request.files["video"]

    path = os.path.join(

        app.config["UPLOAD_FOLDER"],

        file.filename

    )

    file.save(path)

    video_source = path

    if camera is not None:

        camera.release()

    camera = None

    return jsonify({

        "success": True,

        "filename": file.filename

    })

@app.route("/upload_image", methods=["POST"])
def upload_image():

    if "image" not in request.files:

        return jsonify({

            "success": False,

            "message": "Imagem não enviada."

        })

    file = request.files["image"]

    path = os.path.join(

        app.config["UPLOAD_FOLDER"],

        file.filename

    )

    file.save(path)

    return jsonify({

        "success": True,

        "filename": file.filename

    })

def generate_frames():

    global camera

    if camera is None:

        camera = cv2.VideoCapture(video_source)

    while True:

        success, frame = camera.read()

        if not success:

            break

        frame, detections = detector.predict(frame)

        ret, buffer = cv2.imencode(

            ".jpg",

            frame

        )

        frame = buffer.tobytes()

        yield (

            b"--frame\r\n"

            b"Content-Type: image/jpeg\r\n\r\n"

            + frame +

            b"\r\n"

        )


@app.route("/video_feed")
def video_feed():

    return Response(

        generate_frames(),

        mimetype="multipart/x-mixed-replace; boundary=frame"

    )

@app.route("/metrics")
def metrics():

    return jsonify({

        "fps": 0,

        "people": 0,

        "helmet": 0,

        "alerts": 0

    })

if __name__ == "__main__":

    app.run(

        debug=True,

        host="0.0.0.0",

        port=5000

    )