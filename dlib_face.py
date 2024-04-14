# https://www.studytonight.com/post/dlib-68-points-face-landmark-detection-with-opencv-and-python
# USAGE: python facial_68_Landmark.py

import dlib, cv2
import numpy as np


def writeFaceLandmarksToLocalFile(faceLandmarks, fileName):
    with open(fileName, 'w') as f:
        for p in faceLandmarks.parts():
            f.write("%s %s\n" % (int(p.x), int(p.y)))

    f.close()


# This below mehtod will draw all those points which are from 0 to 67 on face one by one.
def drawPoints(image, faceLandmarks, startpoint, endpoint, isClosed=False):
    points = []
    for i in range(startpoint, endpoint + 1):
        point = [faceLandmarks.part(i).x, faceLandmarks.part(i).y]
        points.append(point)

    points = np.array(points, dtype=np.int32)
    cv2.polylines(image, [points], isClosed, (255, 200, 0), thickness=2, lineType=cv2.LINE_8)


# Use this function for 70-points facial landmark detector model
# we are checking if points are exactly equal to 68, then we draw all those points on face one by one
def facePoints(image, faceLandmarks):
    assert (faceLandmarks.num_parts == 68)
    drawPoints(image, faceLandmarks, 0, 16)  # Jaw line
    drawPoints(image, faceLandmarks, 17, 21)  # Left eyebrow
    drawPoints(image, faceLandmarks, 22, 26)  # Right eyebrow
    drawPoints(image, faceLandmarks, 27, 30)  # Nose bridge
    drawPoints(image, faceLandmarks, 30, 35, True)  # Lower nose
    drawPoints(image, faceLandmarks, 36, 41, True)  # Left eye
    drawPoints(image, faceLandmarks, 42, 47, True)  # Right Eye
    drawPoints(image, faceLandmarks, 48, 59, True)  # Outer lip
    drawPoints(image, faceLandmarks, 60, 67, True)  # Inner lip


# Use this function for any model other than
# 70 points facial_landmark detector model
def facePoints2(image, faceLandmarks, color=(0, 255, 0), radius=4):
    for p in faceLandmarks.parts():
        cv2.circle(image, (p.x, p.y), radius, color, -1)


# location of the model (path of the model).
Model_PATH = "shape_predictor_68_face_landmarks.dat"

# now from the dlib we are extracting the method get_frontal_face_detector()
# and assign that object result to frontalFaceDetector to detect face from the image with
# the help of the 68_face_landmarks.dat model
frontalFaceDetector = dlib.get_frontal_face_detector()

# Now the dlip shape_predictor class will take model and with the help of that, it will show
faceLandmarkDetector = dlib.shape_predictor(Model_PATH)

# We now reading image on which we applied our face detector
image = "img.jpg"
# Now we are reading image using openCV
def draw_face(img):
    # img = cv2.imread(image)
    imageRGB = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    # landmarks of the face image  will be stored in output/image_k.txt
    faceLandmarksOuput = "output/image"
    # Now this line will try to detect all faces in an image either 1 or 2 or more faces
    allFaces = frontalFaceDetector(imageRGB, 0)

    print("List of all faces detected: ", len(allFaces))

    # List to store landmarks of all detected faces
    allFacesLandmark = []

    # Below loop we will use to detect all faces one by one and apply landmarks on them

    for k in range(0, len(allFaces)):
        # dlib rectangle class will detecting face so that landmark can apply inside of that area
        faceRectangleDlib = dlib.rectangle(int(allFaces[k].left()), int(allFaces[k].top()),
                                           int(allFaces[k].right()), int(allFaces[k].bottom()))
        # Now we are running loop on every detected face and putting landmark on that with the help of faceLandmarkDetector
        detectedLandmarks = faceLandmarkDetector(imageRGB, faceRectangleDlib)
        # count number of landmarks we actually detected on image
        if k == 0:
            print("Total number of face landmarks detected ", len(detectedLandmarks.parts()))
        # Svaing the landmark one by one to the output folder
        allFacesLandmark.append(detectedLandmarks)
        # Now finally we drawing landmarks on face
        facePoints(img, detectedLandmarks)


    cv2.imshow("Face landmark result", img)


if __name__ == '__main__':
    vid = cv2.VideoCapture(0)
    while True:
        ret, frame = vid.read()
        draw_face(frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
    cv2.destroyAllWindows()

# Pause screen to wait key from user to see result
cv2.waitKey(0)
cv2.destroyAllWindows()
