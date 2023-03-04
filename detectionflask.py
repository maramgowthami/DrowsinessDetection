'''from flask import Flask, render_template, Response, request
import cv2
import datetime, time
import os, sys
import numpy as np
from threading import Thread
#instatiate flask app
app = Flask(__name__, template_folder='./templates')
camera = cv2.VideoCapture(0)
@app.route('/')
def index():
    return render_template('index.html')
@app.route('/')
def capture():
    count = 1

    while True:
        cap.set(cv2.CAP_PROP_POS_MSEC, (count * 100))
        ret, img = cap.read()
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        faces = face_cascade.detectMultiScale(gray, 1.2, 5)
        for (x, y, w, h) in faces:
            cv2.rectangle(img, (x, y), (x + w, y + h), (255, 0, 0), 2)
            roi_gray = gray[y:y + h, x:x + w]
            roi_color = img[y:y + h, x:x + w]

            eyes = eye_cascade.detectMultiScale(roi_gray, 1.3, minSize=(45, 45))
            for (ex, ey, ew, eh) in eyes:
                print(count)
                crop_img = roi_gray[ey: ey + eh, ex: ex + ew]
                cv2.rectangle(roi_color, (ex, ey), (ex + ew, ey + eh), (0, 255, 0), 2)
                s1 = 'newSAVE2/{}.jpg'.format(count)
                count = count + 1
                cv2.imwrite(s1, crop_img)

        cv2.imshow('img', img)
        k = cv2.waitKey(1000) & 0xff
        if k == 7:
            break





if __name__ == '__main__':
    app.run()

camera.release()
cv2.destroyAllWindows()'''
