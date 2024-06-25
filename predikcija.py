import os
import cv2
from ultralytics import YOLO
import sys

def process_image(image_path):
    model_path = os.path.join('.', 'runs', 'detect', 'train', 'weights', 'last.pt')

    # Load a model
    model = YOLO(model_path)  # load a custom model

    threshold = 0.1

    # Read the image
    image = cv2.imread(image_path)

    if image is None:
        print(f"Error opening image: {image_path}")
        return None

    # Make predictions using the model
    results = model(image)[0]

    # Process the results
    for result in results.boxes.data.tolist():
        x1, y1, x2, y2, score, class_id = result

        if score > threshold:
            # Format the confidence score as a percentage (multiply by 100)
            confidence_text = f"{score:.2f}%"  # Format to 2 decimal places

            # Draw bounding box and label with confidence
            cv2.rectangle(image, (int(x1), int(y1)), (int(x2), int(y2)), (0, 255, 0), 4)
            cv2.putText(image, f"{results.names[int(class_id)].upper()} {confidence_text}",
                        (int(x1), int(y1 - 10)), cv2.FONT_HERSHEY_SIMPLEX, 1.3, (0, 255, 0), 3, cv2.LINE_AA)

    # Save the processed image
    processed_image_path = image_path.replace(".", "_obradjena.")
    cv2.imwrite(processed_image_path, image)
    return processed_image_path

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python predikcija.py <image_path>")
        sys.exit(1)

    image_path = sys.argv[1]
    processed_image_path = process_image(image_path)
    if processed_image_path:
        print(f"Processed image saved at: {processed_image_path}")
    else:
        print("Error processing image.")