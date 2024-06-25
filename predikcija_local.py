import os
import cv2
from ultralytics import YOLO

# upisi ime slike
image_path = "1v.jpg"
#6,#3,#4,#5 (ne prepoznaje)
model_path = os.path.join('.', 'runs', 'detect', 'train', 'weights', 'last.pt')

# ucitaj model
model = YOLO(model_path)

threshold = 0.1

# ucitaj sliku
image = cv2.imread(image_path)

if image is None:
    print("greska prilikom ucitavanja slike:", image_path)
    exit()

# rez ekrana na koju prikazujes
screen_width = 1920
screen_height = 1080

# dimenzije slike
image_height, image_width = image.shape[:2]

# kalkulisi prethodno dvoje
scale_width = screen_width / image_width
scale_height = screen_height / image_height
scale = min(scale_width, scale_height)

# napravi kal. za prikazanu sliku
new_width = int(image_width * scale)
new_height = int(image_height * scale)

# prikazi je
resized_image = cv2.resize(image, (new_width, new_height))

# predikcija
results = model(resized_image)[0]

# obradjivanje rezultat
for result in results.boxes.data.tolist():
    x1, y1, x2, y2, score, class_id = result

    if score > threshold:

        confidence_text = f"{score:.2f}%"  # svedi na 2 decimale

        # nacrtaj oko reg i kolko si siguran
        cv2.rectangle(resized_image, (int(x1), int(y1)), (int(x2), int(y2)), (0, 255, 0), 2)
        cv2.putText(resized_image, f"{results.names[int(class_id)].upper()} {confidence_text}",
                    (int(x1), int(y1 - 10)), cv2.FONT_HERSHEY_SIMPLEX, 1.3, (0, 255, 0), 2, cv2.LINE_AA)

#prikazi sliku
cv2.imshow("Image", resized_image)

#
cv2.waitKey(0)

cv2.destroyAllWindows()
