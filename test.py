import cv2
import numpy as np
from ultralytics import YOLO
from flask import Flask

print("OpenCV:", cv2.__version__)
print("NumPy:", np.__version__)

modelo = YOLO("yolov8n.pt")
print("YOLO carregado com sucesso!")

app = Flask(__name__)
print("Flask OK!")