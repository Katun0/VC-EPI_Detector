from ultralytics import YOLO
import cv2

model = YOLO("models/best.pt")
print(model.names)

img = cv2.imread("static/uploads/annotated_images (1).jpg")

results = model(img)

for result in results:

    print("Boxes:", len(result.boxes))

    for box in result.boxes:

        print(
            model.names[int(box.cls[0])],
            float(box.conf[0])
        )

img = results[0].plot()

cv2.imshow("Resultado", img)
cv2.waitKey(0)