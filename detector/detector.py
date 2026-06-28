from ultralytics import YOLO
import cv2
import time
import os

class EPIDetector:

    def __init__(self, model_path=None, confidence=0.2):


        self.ppe_model = YOLO(os.path.join("models", "best.pt"))
        self.person_model = YOLO(os.path.join("models", "yolov8n.pt"))
        self.confidence = confidence

        # nomes das classes do modelo
        self.person_classes = self.person_model.names
        self.ppe_classes = self.ppe_model.names

        print("Classes do modelo PPE:")
        print(self.ppe_model.names)

        print("\nClasses do modelo de pessoas:")
        print(self.person_model.names)

    def detect_ppe(self, frame):

        return self.ppe_model(
            frame,
            conf=self.confidence,
            verbose=False
        )
    
    def detect_persons(self, frame):

        return self.person_model(
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
            "safety_shoe": (128, 0, 255),
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
    
    def split_detections(self, detections):
        persons = []
        epis = []

        for det in detections:

            if det["class"] == "person":

                persons.append(det)

            else:

                epis.append(det)

        return persons, epis
