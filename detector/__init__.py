from .detector import EPIDetector


# from ultralytics import YOLO
# import cv2
# import os


# class EPIDetector:

#     def __init__(self, model_path=None, confidence=0.50):

#         if model_path is None:
#             model_path = "yolov8n.pt"

#         print(f"Carregando modelo: {model_path}")

#         self.model = YOLO(model_path)

#         self.confidence = confidence

#         self.class_names = self.model.names

#     def detect(self, frame):

#         # executa a inferência pra retornar os dados XD
#         results = self.model(
#             frame,
#             conf=self.confidence,
#             verbose=False
#         )

#         return results

#     def draw(self, frame, results):

#         # Esse desenha as bounding boxes na image

#         for result in results:

#             boxes = result.boxes

#             for box in boxes:

#                 x1, y1, x2, y2 = map(int, box.xyxy[0])

#                 confidence = float(box.conf[0])

#                 class_id = int(box.cls[0])

#                 label = self.class_names[class_id]

#                 color = self.get_color(label)

#                 cv2.rectangle(
#                     frame,
#                     (x1, y1),
#                     (x2, y2),
#                     color,
#                     2
#                 )

#                 text = f"{label} {confidence:.2f}"

#                 cv2.putText(
#                     frame,
#                     text,
#                     (x1, y1 - 10),
#                     cv2.FONT_HERSHEY_SIMPLEX,
#                     0.6,
#                     color,
#                     2
#                 )

#         return frame

#     def predict(self, frame):

#         # Eecuta a inferência

#         results = self.detect(frame)

#         annotated = self.draw(frame.copy(), results)

#         return annotated, results

#     @staticmethod
#     def get_color(label):

#         colors = {

#         "person": (255,255,0),

#         "helmet": (0,255,0),

#         "goggles": (255,0,255),

#         "vest": (0,255,255),

#         "mask": (255,0,0),

#         "gloves": (0,165,255),

#         "boots": (128,0,255)

#     }

#         return colors.get(label, (255, 255, 255))
    
#     # Esse init agora facilita a importação, agora é só fazer "from detector import EPIDetector"