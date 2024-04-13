import numpy as np
import cv2

import time #for camera setup time

videoCap = cv2.VideoCapture(0) #capture the video from 1st webcam

time.sleep(3) #2 sec for the camera to setup

background = 0 #background that I have to display when I have the cloth on myself

for i in range(60): #30 iteration to capture the background
    ret, background = videoCap.read()

while(videoCap.isOpened()):
    ret, img = videoCap.read()

    if not ret:
        break

    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)

    lower_red = np.array([0, 120, 70])
    upper_red = np.array([10, 255, 255])
    mask1 = cv2.inRange(hsv, lower_red, upper_red) #seperating/segmenting the cloak part

    lower_red = np.array([170, 120, 70])
    upper_red = np.array([180, 255, 255])
    mask2 = cv2.inRange(hsv, lower_red, upper_red)

    mask1 = mask1 + mask2 # 1 or 2 i.e any shade of red between mask1 and mask2 then we need to segment that part

    mask1 = cv2.morphologyEx(mask1, cv2.MORPH_OPEN, np.ones((3,3), np.uint8), iterations=2) #noise Removal
    mask1 = cv2.morphologyEx(mask1, cv2.MORPH_DILATE, np.ones((3,3), np.uint8), iterations=1)

    mask2 = cv2.bitwise_not(mask1) # mask2 == everything except the cloak

    res1 = cv2.bitwise_and(background, background, mask=mask1) #Used for segmentation of the color
    res2 = cv2.bitwise_and(img, img, mask=mask2) #used to substitute the cloak part
    final_output = cv2.addWeighted(res1, 1, res2, 1, 0) #superimposing 2 images

    cv2.imshow('We did it !!', final_output)
    k = cv2.waitKey(10)
    if k == 27:
        break

    videoCap.release()
    cv2.destroyAllWindows()