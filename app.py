from flask import Flask, render_template, Response, request, jsonify, url_for
from detector import EPIDetector, ImageProcessor, MetricsTracker, ComplianceChecker

import matplotlib
matplotlib.use("Agg")  # backend sem GUI, para renderizar PNG no servidor
import matplotlib.pyplot as plt

import cv2
import os
import io 
import threading

app = Flask(__name__)

UPLOAD_FOLDER = "static/uploads"    
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

# Componentes do sistema
detector = EPIDetector()
processor = ImageProcessor()
metrics = MetricsTracker()
compliance_checker = ComplianceChecker()

camera = None
video_source = 0
last_frame = None  # último frame lido (usado em /processing_demo)
frame_lock = threading.Lock()


@app.route("/")
def index():
    return render_template("index.html")


# @app.route("/start_webcam")
# def start_webcam():

#     global camera, video_source

#     video_source = 0
#     if camera is not None:
#         camera.release()
#     camera = None

#     metrics.reset()

#     return jsonify({"success": True})

# @app.route("/stop_webcam")
# def stop_webcam():
#     return

@app.route("/upload_video", methods=["POST"])
def upload_video():

    global camera, video_source

    if "video" not in request.files:
        return jsonify({"success": False, "message": "Vídeo não enviado."})

    file = request.files["video"]
    path = os.path.join(app.config["UPLOAD_FOLDER"], file.filename)
    file.save(path)

    video_source = path
    if camera is not None:
        camera.release()
    camera = None

    metrics.reset()

    return jsonify({"success": True, "filename": file.filename})


@app.route("/upload_image", methods=["POST"])
def upload_image():

    if "image" not in request.files:
        return jsonify({"success": False, "message": "Imagem não enviada."})

    file = request.files["image"]
    path = os.path.join(app.config["UPLOAD_FOLDER"], file.filename)
    file.save(path)

    image = cv2.imread(path)
    global last_frame

    with frame_lock:
        last_frame = image.copy()
        
    MAX_WIDTH = 1280
    MAX_HEIGHT = 720

    h, w = image.shape[:2]

    scale = min(
        MAX_WIDTH / w,
        MAX_HEIGHT / h,
        1.0
    )

    if scale < 1:

        image = cv2.resize(
            image,
            (int(w * scale), int(h * scale)),
            interpolation=cv2.INTER_AREA
        )
    if image is None:
        return jsonify({"success": False, "message": "Não foi possível ler a imagem."})

    annotated, detections, inference_ms, compliance = detector.predict(
        image, checker=compliance_checker
    )
    metrics.reset()

    metrics.update(
        inference_ms,
        detections,
        compliance
    )

    # salva a imagem anotada
    out_name = f"annotated_{file.filename}"
    out_path = os.path.join(app.config["UPLOAD_FOLDER"], out_name)
    cv2.imwrite(out_path, annotated)

    return jsonify({
        "success": True,
        "filename": file.filename,
        "annotated_url": url_for("static", filename=f"uploads/{out_name}"),
        "inference_ms": round(inference_ms, 1),
        "counts": detector.count_classes(detections),
        "compliance": compliance,
    })


def generate_frames():

    global camera, last_frame

    if camera is None:
        camera = cv2.VideoCapture(video_source)

    if not camera.isOpened():
        print("[ERRO] Não foi possível abrir a fonte de vídeo.")
        return

    while True:

        success, frame = camera.read()
        h, w = frame.shape[:2]

        scale = min(
        1280 / w,
        720 / h
        )

        frame = cv2.resize(
            frame,
            (int(w * scale), int(h * scale))
        )
        if not success:
            break

        annotated, detections, inference_ms, compliance = detector.predict(
            frame, checker=compliance_checker
        )

        metrics.update(inference_ms, detections, compliance)

        with frame_lock:
            last_frame = frame.copy()

        ret, buffer = cv2.imencode(".jpg", annotated)
        if not ret:
            continue

        yield (
            b"--frame\r\n"
            b"Content-Type: image/jpeg\r\n\r\n"
            + buffer.tobytes() +
            b"\r\n"
        )

    if camera is not None:
        camera.release()
        camera = None


@app.route("/video_feed")
def video_feed():
    return Response(
        generate_frames(),
        mimetype="multipart/x-mixed-replace; boundary=frame"
    )


@app.route("/metrics")
def get_metrics():
    return jsonify(metrics.snapshot())


@app.route("/reset", methods=["POST"])
def reset():

    global last_frame, camera

    metrics.reset()

    with frame_lock:
        last_frame = None

    if camera is not None:
        camera.release()
        camera = None

    return jsonify({"success": True})


@app.route("/processing_demo")
def processing_demo():
    """Mosaico com as etapas de processamento de imagem do último frame."""
    with frame_lock:
        frame = None if last_frame is None else last_frame.copy()

    if frame is None:
        # imagem placeholder simples se ainda não há frame
        return Response(status=204)

    grid = processor.debug_grid(frame)
    ret, buffer = cv2.imencode(".png", grid)
    return Response(buffer.tobytes(), mimetype="image/png")


@app.route("/report.png")
def report():
    # Gráfico Matplotlib com distribuição de detecções e desempenho.
    snap = metrics.snapshot()

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(10, 4))
    fig.patch.set_facecolor("#1e293b")

    # Distribuição por classe
    counts = snap["class_counts"]
    if counts:
        labels = list(counts.keys())
        values = list(counts.values())
        ax1.bar(labels, values, color="#38bdf8")
    ax1.set_title("Detecções por classe", color="#f8fafc")
    ax1.tick_params(colors="#94a3b8")
    ax1.set_facecolor("#0f172a")

    # Indicadores de desempenho/conformidade
    perf_labels = ["FPS", "Inferência (ms)", "Conformes", "Não Conf."]
    perf_values = [
        snap["fps"],
        snap["inference_ms"],
        snap["compliant"],
        snap["non_compliant"],
    ]
    ax2.bar(perf_labels, perf_values,
            color=["#38bdf8", "#facc15", "#10b981", "#ef4444"])
    ax2.set_title("Desempenho e conformidade", color="#f8fafc")
    ax2.tick_params(colors="#94a3b8", labelrotation=20)
    ax2.set_facecolor("#0f172a")

    fig.tight_layout()

    buf = io.BytesIO()
    fig.savefig(buf, format="png", facecolor=fig.get_facecolor())
    plt.close(fig)
    buf.seek(0)

    return Response(buf.getvalue(), mimetype="image/png")


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)
