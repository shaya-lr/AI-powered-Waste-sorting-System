import cv2
import numpy as np
from tensorflow.keras.models import load_model
import requests


#https://blynk.cloud/external/api/update?token=Xqn7W0j_dLkonNrI6mIw40FqLP4OFR9h&V4=bio
def update_data_to_blynk(value):
    iot_url = f"https://blynk.cloud/external/api/update?token=Xqn7W0j_dLkonNrI6mIw40FqLP4OFR9h&V4={value}"
    try:
        response = requests.get(iot_url)
        if response.status_code == 200:
            print("Data sent successfully to Blynk.")
        else:
            print(f"Failed to send data to Blynk. Status code: {response.status_code}")
    except Exception as e:
        print(f"Error: {e}")

# Load the trained model
model_path = "cnn_model.h5"  # Path to your trained model
model = load_model(model_path)

# Map class indices to class names
class_indices = {'biodegradable': 0, 'non_biodegradable': 1}
class_names = {v: k for k, v in class_indices.items()}

# Parameters for input image preprocessing
IMG_HEIGHT, IMG_WIDTH = 150, 150  # Match the input size of your model

# Function to preprocess the frame
def preprocess_frame(frame):
    img = cv2.resize(frame, (IMG_WIDTH, IMG_HEIGHT))  # Resize to model input size
    img = img.astype("float32") / 255.0  # Normalize pixel values
    img = np.expand_dims(img, axis=0)  # Add batch dimension
    return img

# Open webcam
cap = cv2.VideoCapture(0)

if not cap.isOpened():
    print("Error: Could not open webcam.")
    exit()

print("Press 'SPACE' to capture an image and predict.")
print("Press 'q' to quit.")

while True:
    # Capture frame from webcam
    ret, frame = cap.read()
    if not ret:
        print("Error: Could not read frame.")
        break

    # Show the live webcam feed
    cv2.imshow("Webcam Feed", frame)

    # Check for key press
    key = cv2.waitKey(1) & 0xFF

    if key == ord(' '):  # Spacebar to capture and predict
        # Preprocess the captured frame
        preprocessed_frame = preprocess_frame(frame)

        # Predict class
        predictions = model.predict(preprocessed_frame)
        predicted_class_index = np.argmax(predictions[0])  # Get the class with highest probability
        confidence = predictions[0][predicted_class_index]  # Confidence of prediction
        predicted_class_name = class_names[predicted_class_index]

        # Display the prediction result
        print(f"Captured Image Prediction: {predicted_class_name} (Confidence: {confidence:.2f})")

        # Display result on the captured frame
        result_text = f"Class: {predicted_class_name}, Confidence: {confidence:.2f}"
        cv2.putText(frame, result_text, (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)
        cv2.imshow("Captured Image", frame)

        #update to blynk cloud
        update_data_to_blynk(predicted_class_name)

    if key == ord('q'):  # Quit the application
        break

# Release resources
cap.release()
cv2.destroyAllWindows()
