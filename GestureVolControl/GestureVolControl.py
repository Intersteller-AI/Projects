import cv2
import mediapipe as mp
import time
import numpy as np
from cv2 import waitKey
from HandTracking import handDetector
from ctypes import cast, POINTER
from comtypes import CLSCTX_ALL
from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume
from cv2 import VideoCapture



# capture video from camera
cap = VideoCapture(0)

# set the width and height of our web cam
wCam, hCam = 640, 480

cap.set(3, wCam)
cap.set(4, hCam)

pTime = 0

# make object of HandDetector class
detector = handDetector(detectionCon=0.7)

# create the utilities for the volume control
devices = AudioUtilities.GetSpeakers()
interface = devices.Activate(
    IAudioEndpointVolume._iid_, CLSCTX_ALL, None)

volume_ = cast(interface, POINTER(IAudioEndpointVolume))
volRange = volume_.GetVolumeRange()
minVol = volRange[0]
maxVol = volRange[1]
vol = 0
volBar = 400
volper = 0
print(volRange)
print(volume_)

# start reading the image
while True:
    _, img = cap.read()

    img = detector.findHands(img, draw=False)
    lmlist = detector.findPosition(img, draw=False)
    if len(lmlist) != 0:
        # print(lmlist[0:14])
        x1, y1 = lmlist[4][1],lmlist[4][2]
        x2, y2 = lmlist[8][1],lmlist[8][2]
        cx, cy = (x1+x2)//2, (y1+y2)//2

        cv2.circle(img, (x1, y1), 9, (0, 255, 0), cv2.FILLED)
        cv2.circle(img, (x2, y2), 9, (0, 255, 0), cv2.FILLED)
        cv2.line(img, (x1, y1), (x2, y2), (0, 0, 255), 3)
        cv2.circle(img, (cx, cy), 9, (255, 0, 0), cv2.FILLED)
        
        length = np.hypot(x2-x1, y2-y1)
        if length < 50:
            cv2.circle(img, (cx, cy), 9, (0, 0, 255), cv2.FILLED)
        vol = np.interp(length, [50, 300], [minVol, maxVol])
        volBar = np.interp(length, [50, 300], [400, 150])
        volper = np.interp(length, [50, 300], [0, 100])
        print(int(length), vol)
        volume_.SetMasterVolumeLevel(vol, None)
        if length == 50:
            cv2.circle(img, (cx, cy), 15, (0, 255, 0), cv2.FILLED)
    cv2.rectangle(img, (50, 150), (85, 400), (255, 0, 0), 3)
    cv2.rectangle(img, (50, int(volBar)), (85, 400), (255, 0, 0), cv2.FILLED)
    cv2.putText(img, f'{int(volper)} %', (40, 450), cv2.FONT_HERSHEY_COMPLEX,
                1, (255, 0, 0), 3)
        

    cTime = time.time()
    fps = 1 / (cTime - pTime)
    pTime = cTime
    cv2.putText(img, f'{int(fps)} FPS', (10, 70), cv2.FONT_HERSHEY_PLAIN, 4, (0, 255, 0), 3)

    cv2.namedWindow("image", cv2.WINDOW_FREERATIO)
    cv2.imshow("image", img)

    if waitKey(1) & 0xFF == ord('q'):
        break

cv2.destroyAllWindows()
