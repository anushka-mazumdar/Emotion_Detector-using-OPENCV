import streamlit as st
import cv2
import numpy as np
from keras.models import load_model
from keras.preprocessing import image

# Load your trained model
model = load_model("best_model.h5")

# Haarcascade for face detection
face_haar_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')

# Define emotions
emotions = ('angry', 'disgust', 'fear', 'happy', 'sad', 'surprise', 'neutral')

# Initialize session state for video recording
if "video_active" not in st.session_state:
    st.session_state.video_active = False

# App Layout
st.set_page_config(page_title="Emotion Detector", layout="wide")
st.title("Real-Time Emotion Detection")
st.markdown("This app uses a deep learning model to detect emotions from live video.")

# Sidebar controls
st.sidebar.header("Controls")
start_video = st.sidebar.button("Start Live Video Emotion Detection")
stop_video = st.sidebar.button("Stop Live Recording")

# Function to start live video recording
def start_live_video():
    cap = cv2.VideoCapture(0)  # Open webcam
    if not cap.isOpened():
        st.error("Unable to access the webcam. Please check your camera settings.")
        return

    stframe = st.empty()  # Placeholder for video display

    while st.session_state.video_active:
        ret, test_img = cap.read()
        if not ret:
            st.error("Failed to capture video. Exiting...")
            break

        # Convert to grayscale and detect faces
        gray_img = cv2.cvtColor(test_img, cv2.COLOR_BGR2GRAY)
        faces_detected = face_haar_cascade.detectMultiScale(gray_img, scaleFactor=1.3, minNeighbors=5)

        for (x, y, w, h) in faces_detected:
            # Draw rectangle around face
            cv2.rectangle(test_img, (x, y), (x + w, y + h), (255, 0, 0), thickness=2)

            # Prepare region of interest
            roi_gray = gray_img[y:y + h, x:x + w]
            roi_gray = cv2.resize(roi_gray, (224, 224))
            roi_gray = cv2.cvtColor(roi_gray, cv2.COLOR_GRAY2RGB)
            img_pixels = image.img_to_array(roi_gray)
            img_pixels = np.expand_dims(img_pixels, axis=0)
            img_pixels /= 255.0

            # Predict emotion
            predictions = model.predict(img_pixels)
            max_index = np.argmax(predictions[0])
            predicted_emotion = emotions[max_index]

            # Display emotion label
            cv2.putText(test_img, predicted_emotion, (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 255, 0), 2)

        # Display video in Streamlit
        frame = cv2.cvtColor(test_img, cv2.COLOR_BGR2RGB)
        stframe.image(frame, channels="RGB", use_column_width=True)

        # Stop if "Stop Live Recording" is clicked
        if not st.session_state.video_active:
            break

    cap.release()
    cv2.destroyAllWindows()
    st.warning("Live video stopped.")

# Handle button actions
if start_video and not st.session_state.video_active:
    st.session_state.video_active = True
    st.info("Live video started. Click 'Stop Live Recording' to exit.")
    start_live_video()

if stop_video:
    st.session_state.video_active = False
    st.warning("Live video recording stopped.")
