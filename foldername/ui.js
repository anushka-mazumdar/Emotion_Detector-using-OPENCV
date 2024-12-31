const video = document.getElementById('video');
const startCamera = document.getElementById('startCamera');
const stopCamera = document.getElementById('stopCamera');
const emotionText = document.getElementById('emotionText');

let videoStream = null; // Store the video stream
let intervalId = null;  // Store the interval ID

startCamera.addEventListener('click', async () => {
    if (navigator.mediaDevices && navigator.mediaDevices.getUserMedia) {
        try {
            const stream = await navigator.mediaDevices.getUserMedia({ video: true });
            video.srcObject = stream;
            videoStream = stream; // Save the stream for later use

            // Prepare canvas for capturing video frames
            const canvas = document.createElement('canvas');
            const context = canvas.getContext('2d');

            // Send frames periodically to the backend
            intervalId = setInterval(async () => {
                canvas.width = video.videoWidth;
                canvas.height = video.videoHeight;
                context.drawImage(video, 0, 0, canvas.width, canvas.height);
                const frame = canvas.toDataURL('image/jpeg');

                try {
                    const response = await fetch('http://127.0.0.1:5000/detect', {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json',
                        },
                        body: JSON.stringify({ image: frame }),
                    });
                    const data = await response.json();
                    if (data.emotion) {
                        emotionText.textContent = data.emotion;
                    } else {
                        emotionText.textContent = 'No Emotion Detected';
                    }
                } catch (err) {
                    console.error('Error communicating with backend:', err);
                    emotionText.textContent = 'Error detecting emotion';
                }
            }, 2000); // Send every 2 seconds
        } catch (error) {
            console.error('Error accessing the camera:', error);
            alert('Unable to access camera. Please check permissions.');
        }
    } else {
        alert('Camera not supported on this browser.');
    }
});

stopCamera.addEventListener('click', () => {
    // Stop the video stream
    if (videoStream) {
        const tracks = videoStream.getTracks();
        tracks.forEach((track) => {
            track.stop(); // Stop each track
        });
        videoStream = null; // Remove reference to the video stream
    }

    // Stop sending frames to the backend
    if (intervalId) {
        clearInterval(intervalId); // Clear the interval
        intervalId = null;
    }

    // Reset the video element and UI
    video.srcObject = null; // Disconnect the video element from the stream
    video.load(); // Reset the video element completely
    emotionText.textContent = 'None'; // Reset detected emotion text
});
