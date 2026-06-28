from ultralytics import YOLO
import cv2
import time
import os

class EPIDetector:

    def __init__(self, model_path=None, confidence=0.5):

        # Procura primeiro um modelo treinado em EPIs (best.pt); se não houver,
        # usa o YOLOv8n base (detecta pessoas e serve de fallback).
        if model_path is None:
            candidates = [
                os.path.join("models", "best.pt"),
                os.path.join("models", "yolov8n.pt"),
                "yolov8n.pt",
            ]
            model_path = next((c for c in candidates if os.path.exists(c)),
                              "yolov8n.pt")

        print(f"[INFO] Carregando modelo: {model_path}")

        self.model = YOLO(model_path)
        self.personmodel = YOLO(os.path.join("models", "yolov8n.pt"))
        self.confidence = confidence

        # nomes das classes do modelo
        self.class_names = self.model.names

    def detect_ppe(self, frame):

        return self.model(
            frame,
            conf=self.confidence,
            verbose=False
        )
    
    def detect_persons(self, frame):

        return self.personmodel(
            frame,
            conf=self.confidence,
            classes=[0],          # apenas person
            verbose=False
        )

    def draw(self, frame, detections, compliance=None):

        # Pré-mapeia o status de cada pessoa pela sua bbox, para colorir
        # a caixa de acordo com a conformidade.
        person_status = {}
        if compliance is not None:
            for person in compliance.get("persons", []):
                person_status[tuple(person["bbox"])] = person["status"]

        for det in detections:

            x1, y1, x2, y2 = det["bbox"]
            label = det["class"].lower()
            confidence = det["confidence"]

            if label == "person" and tuple(det["bbox"]) in person_status:
                status = person_status[tuple(det["bbox"])]
                color = (0, 200, 0) if status == "Conforme" else (0, 0, 255)
                text = f"{label} - {status} {confidence:.2f}"
            else:
                color = self.get_color(label)
                text = f"{label} {confidence:.2f}"

            cv2.rectangle(frame, (x1, y1), (x2, y2), color, 2)

            cv2.putText(
                frame,
                text,
                (x1, max(y1 - 10, 15)),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.6,
                color,
                2
            )

        return frame

    def predict(self, frame, checker=None):
        """
        Processa um frame: detecta, (opcionalmente) verifica conformidade e
        desenha o resultado.

        Retorna: (frame_anotado, detections, inference_ms, compliance)
        """
        start = time.perf_counter()

        person_results = self.detect_persons(frame)

        ppe_results = self.detect_ppe(frame)

        inference_ms = (
            time.perf_counter() - start
        ) * 1000

        detections = []
        for result in person_results:
            for box in result.boxes:
                detections.append({
                    "class":"person",
                    "confidence": float(box.conf[0]),
                    "bbox": list(map(int, box.xyxy[0])),
                })

        for result in ppe_results:
            for box in result.boxes:

                detections.append({

                    "class":self.ppe_classes[
                        int(box.cls[0])
                    ].lower(),

                    "confidence":float(box.conf[0]),

                    "bbox":list(map(int,box.xyxy[0]))

                })

        compliance = checker.check(detections) if checker is not None else None

        annotated = self.draw(frame.copy(), detections, compliance)

        return annotated, detections, inference_ms, compliance

    @staticmethod
    def get_color(label):

        colors = {
            "person": (255, 255, 0),
            "helmet": (0, 255, 0),
            "hardhat": (0, 255, 0),
            "goggles": (255, 0, 255),
            "vest": (0, 255, 255),
            "mask": (255, 0, 0),
            "gloves": (0, 165, 255),
            "boots": (128, 0, 255),
        }

        return colors.get(label.lower(), (255, 255, 255))

    def count_classes(self, detections):

        counts = {}
        for det in detections:
            cls = det["class"]
            counts[cls] = counts.get(cls, 0) + 1
        return counts

    def get_persons(self, detections):

        return [
            det for det in detections
            if det["class"] == "person"
        ]
