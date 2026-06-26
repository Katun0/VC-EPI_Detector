from ultralytics import YOLO
import cv2


class EPIDetector:

    def __init__(self, model_path=None, confidence=0.5):

        # pra ficar melhor, se não identificar o modelo ele puxa direto o YOLO
        if model_path is None:
            model_path = "yolov8n.pt"

        print(f"[INFO] Carregando modelo: {model_path}")

        self.model = YOLO(model_path)
        self.confidence = confidence

        # nomes das classes do modelo
        self.class_names = self.model.names

    def detect(self, frame):

        results = self.model(
            frame,
            conf=self.confidence,
            verbose=False
        )

        return results
    
    def draw(self, frame, results):

        for result in results:

            boxes = result.boxes

            for box in boxes:

                x1, y1, x2, y2 = map(int, box.xyxy[0])

                confidence = float(box.conf[0])

                class_id = int(box.cls[0])

                label = self.class_names[class_id].lower()

                color = self.get_color(label)

                # bounding box
                cv2.rectangle(
                    frame,
                    (x1, y1),
                    (x2, y2),
                    color,
                    2
                )

                text = f"{label} {confidence:.2f}"

                cv2.putText(
                    frame,
                    text,
                    (x1, y1 - 10),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.6,
                    color,
                    2
                )

        return frame

    def predict(self, frame):

        results = self.detect(frame)

        annotated = self.draw(frame.copy(), results)

        detections = []

        for result in results:

            for box in result.boxes:

                detections.append({

                    "class": self.class_names[int(box.cls[0])].lower(),

                    "confidence": float(box.conf[0]),

                    "bbox": list(map(int, box.xyxy[0]))

                })

        return annotated, detections

    @staticmethod
    def get_color(label):

        colors = {

            "person": (255, 255, 0),
            "helmet": (0, 255, 0),
            "goggles": (255, 0, 255),
            "vest": (0, 255, 255),
            "mask": (255, 0, 0),
            "gloves": (0, 165, 255),
            "boots": (128, 0, 255)

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