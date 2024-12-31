from flask import Flask, request, jsonify
from PIL import Image
import numpy as np
import base64
import cv2
import io
from flask_cors import CORS
from keras.models import load_model

app = Flask(__name__)
CORS(app)  # Allow cross-origin requests
model = load_model("best_model.h5")
face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')

emotions = ['angry', 'disgust', 'fear', 'happy', 'sad', 'surprise', 'neutral']

@app.route('/detect', methods=['POST'])
def detect_emotion():
    try:
        data = request.json
        image_data = data['image']
        image_data = base64.b64decode(image_data.split(',')[1])
        image = Image.open(io.BytesIO(image_data))
        image = np.array(image)

        gray_img = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        faces = face_cascade.detectMultiScale(gray_img, scaleFactor=1.3, minNeighbors=5)

        if len(faces) == 0:
            return jsonify({'emotion': 'No Face Detected'})

        for (x, y, w, h) in faces:
            roi_gray = gray_img[y:y + h, x:x + w]
            roi_gray = cv2.resize(roi_gray, (224, 224))
            roi_gray = cv2.cvtColor(roi_gray, cv2.COLOR_GRAY2RGB)
            img_pixels = np.expand_dims(roi_gray, axis=0) / 255.0
            prediction = model.predict(img_pixels)
            max_index = np.argmax(prediction[0])
            detected_emotion = emotions[max_index]
            return jsonify({'emotion': detected_emotion})
    except Exception as e:
        return jsonify({'error': str(e)})

if __name__ == '__main__':
    app.run(debug=True)
