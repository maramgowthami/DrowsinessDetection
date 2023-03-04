from flask import Flask, render_template, Response
#Import necessary libraries
from scipy.spatial import distance
from imutils import face_utils
import numpy as np
import pygame #For playing sound
import time
import dlib
import cv2

#Initialize Pygame and load music
pygame.mixer.init()
pygame.mixer.music.load('audio_alert.wav')

#Minimum threshold of eye aspect ratio below which alarm is triggerd
EYE_ASPECT_RATIO_THRESHOLD = 0.3

#Minimum consecutive frames for which eye ratio is below threshold for alarm to be triggered
EYE_ASPECT_RATIO_CONSEC_FRAMES = 50

## Another constant which will work as a threshold for MAR value
MAR_THRESHOLD = 50

#COunts no. of consecutuve frames below threshold value
COUNTER1 = 0
COUNTER2  =0

#Load face cascade which will be used to draw a rectangle around detected faces.
face_cascade = cv2.CascadeClassifier("haarcascade_frontalface_default.xml")

#This function calculates and return eye aspect ratio
def eye_aspect_ratio(eye):
    A = distance.euclidean(eye[1], eye[5])
    B = distance.euclidean(eye[2], eye[4])
    C = distance.euclidean(eye[0], eye[3])

    ear = (A+B) / (2*C)
    return ear

def mouth_aspect_ratio(mouth):
	A = distance.euclidean(mouth[13], mouth[19])
	B = distance.euclidean(mouth[14], mouth[18])
	C = distance.euclidean(mouth[15], mouth[17])

	MAR = (A + B + C) / 3.0
	return MAR

#Load face detector and predictor, uses dlib shape predictor file
detector = dlib.get_frontal_face_detector()
predictor = dlib.shape_predictor('shape_predictor_68_face_landmarks.dat')

#Extract indexes of facial landmarks for the left and right eye
(lStart, lEnd) = face_utils.FACIAL_LANDMARKS_IDXS['left_eye']
(rStart, rEnd) = face_utils.FACIAL_LANDMARKS_IDXS['right_eye']

## mouth
(mstart, mend) = face_utils.FACIAL_LANDMARKS_IDXS["mouth"]

app = Flask(__name__)

@app.route('/')
def login():
    return render_template('login.html')

#Start webcam video capture
video_capture = cv2.VideoCapture(0)


def generate_frames():
    while True:
        ## read the camera frame
        success,frame = video_capture.read()
        if not success:
            break
        else:
            global COUNTER1, COUNTER2
            # Give some time for camera to initialize(not required)
            time.sleep(2)
            # Read each frame and flip it, and convert to grayscale
            ret, frame = video_capture.read()
            frame = cv2.flip(frame, 1)
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

            # Detect facial points through detector function
            faces = detector(gray, 0)

            # Detect faces through haarcascade_frontalface_default.xml
            face_rectangle = face_cascade.detectMultiScale(gray, 1.3, 5)

            # Draw rectangle around each face detected
            for (x, y, w, h) in face_rectangle:
                cv2.rectangle(frame, (x, y), (x + w, y + h), (255, 0, 0), 2)

            # Detect facial points
            for face in faces:

                shape = predictor(gray, face)
                shape = face_utils.shape_to_np(shape)

                # Get array of coordinates of leftEye and rightEye
                leftEye = shape[lStart:lEnd]
                rightEye = shape[rStart:rEnd]
                mouth = shape[mstart:mend]
                # Calculate aspect ratio of both eyes
                leftEyeAspectRatio = eye_aspect_ratio(leftEye)
                rightEyeAspectRatio = eye_aspect_ratio(rightEye)

                eyeAspectRatio = (leftEyeAspectRatio + rightEyeAspectRatio) / 2

                # Use hull to remove convex contour discrepencies and draw eye shape around eyes
                leftEyeHull = cv2.convexHull(leftEye)
                rightEyeHull = cv2.convexHull(rightEye)
                cv2.drawContours(frame, [leftEyeHull], -1, (0, 255, 0), 1)
                cv2.drawContours(frame, [rightEyeHull], -1, (0, 255, 0), 1)
                cv2.drawContours(frame, [mouth], -1, (0, 255, 0), 1)

                MAR = mouth_aspect_ratio(mouth)
                # Detect if eye aspect ratio is less than threshold
                if (eyeAspectRatio < EYE_ASPECT_RATIO_THRESHOLD):
                    COUNTER1 += 1
                    # If no. of frames is greater than threshold frames,
                    if COUNTER1 >= EYE_ASPECT_RATIO_CONSEC_FRAMES:
                        pygame.mixer.music.play(-1)
                        cv2.putText(frame, "You are Drowsy", (150, 200), cv2.FONT_HERSHEY_SIMPLEX, 1.5, (0, 0, 255),
                                    2)
                else:
                    pygame.mixer.music.stop()
                    COUNTER1 = 0

                if MAR > MAR_THRESHOLD:
                    COUNTER2 += 1
                    pygame.mixer.music.play(-1)
                    cv2.putText(frame, "You are Drowsy", (150, 200), cv2.FONT_HERSHEY_SIMPLEX, 1.5, (0, 0, 255), 2)
                else:
                    pygame.mixer.music.stop()
                    COUNTER2 = 0

            # Show video feed
            cv2.imshow('Video', frame)
            if (cv2.waitKey(1) & 0xFF == ord('q')):
                break

        ret, buffer = cv2.imencode('.jpg', frame)
        frame = buffer.tobytes()

        yield (b'--frame\r\n' b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')


@app.route('/video')
def video1():
    return render_template("index.html")

@app.route('/video1')
def video():
    return Response(generate_frames(),mimetype='multipart/x-mixed-replace; boundary=frame')


@app.route('/map')
def Map():
    return render_template("Map.html")


if __name__ == "__main__":
    app.run(debug=True)

cv2.destroyAllWindows()
video_capture.release()