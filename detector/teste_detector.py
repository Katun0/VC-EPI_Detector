import cv2

from detector import EPIDetector

detector = EPIDetector(
    model_path="yolov8n.pt",
    confidence=0.5
)

imagem = cv2.imread("tem que testar depois com uma imagem")

resultado, detections = detector.predict(imagem)

cv2.imshow("Resultado", resultado)

cv2.waitKey(0)

cv2.destroyAllWindows()