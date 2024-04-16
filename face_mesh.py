import time
from random import shuffle

import cv2
import mediapipe as mp

ABRAKADABRA = False

if ABRAKADABRA:
    from mediapipe.python.solutions.face_mesh_connections import FACEMESH_LEFT_EYE, FACEMESH_LEFT_EYEBROW, \
        FACEMESH_RIGHT_EYE, FACEMESH_RIGHT_EYEBROW, FACEMESH_FACE_OVAL, FACEMESH_NOSE, FACEMESH_RIGHT_IRIS, \
        FACEMESH_LEFT_IRIS
    from face_mesh_connections import _LIP_TOP as LIP_TOP, _LIP_BOTTOM as LIP_BOTTOM
else:
    from face_mesh_connections import FACEMESH_LEFT_EYE, FACEMESH_LEFT_EYEBROW, \
        FACEMESH_RIGHT_EYE, FACEMESH_RIGHT_EYEBROW, FACEMESH_FACE_OVAL, FACEMESH_NOSE, FACEMESH_RIGHT_IRIS, \
        FACEMESH_LEFT_IRIS, LIP_TOP, LIP_BOTTOM

# Face Mesh
mp_draw = mp.solutions.drawing_utils
mp_face_mesh = mp.solutions.face_mesh
face_mesh = mp_face_mesh.FaceMesh(static_image_mode=False,
                                  max_num_faces=1,
                                  refine_landmarks=True,
                                  min_detection_confidence=0.5)
_img = cv2.imread("img.jpg")
DEBUG_CAM_IS_IMG = False


def get_face_points(image):
    height, width, _ = image.shape
    rgb_image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    return face_mesh.process(rgb_image)


def shuffle_contours():
    global contours
    for x in contours:
        shuffle(x)


contours = [FACEMESH_FACE_OVAL, LIP_TOP, LIP_BOTTOM, FACEMESH_LEFT_EYE, FACEMESH_RIGHT_EYE, FACEMESH_LEFT_EYEBROW,
            FACEMESH_RIGHT_EYEBROW, FACEMESH_NOSE, FACEMESH_LEFT_IRIS, FACEMESH_RIGHT_IRIS]


# contours_lines = []
# for contour in contours:
#     d = dict(contour)
#     lines = []
#     line = []
#     for i in range(len(contour) - 1):
#         k1, k2 = contour[i]
#         line.append(k1)
#         if contour[i + 1][0] != k2:
#             if k2 in d:
#                 line.append(d[k2])
#             lines.append(line)
#             line = []
#         else:
#             k = k2
#     if line:
#         lines.append(line)  # edit
#     print(lines)
#

# exit()

def get_face_mash(image, get_all_points=False):
    result = get_face_points(image)
    if result.multi_face_landmarks:
        mfl0 = list(result.multi_face_landmarks)[0]
        # print(len(list(mfl0.landmark)))
        res = [[(mfl0.landmark[i1], mfl0.landmark[i2]) for i1, i2 in fig] for fig in contours]
        if get_all_points:
            return res, mfl0.landmark
        return res
    if get_all_points:
        return [[]], None
    return [[]]


def draw_contours(img, figures):
    height, width, _ = img.shape
    for points in figures:
        for pt1, pt2 in points:
            x = int(pt1.x * width)
            y = int(pt1.y * height)
            x2 = int(pt2.x * width)
            y2 = int(pt2.y * height)

            cv2.circle(img, (x, y), 1, (0, 0, 0), 2)
            cv2.circle(img, (x2, y2), 1, (0, 0, 0), 2)

            cv2.line(img, (x, y), (x2, y2), (0, 100, 0), 2)

            # draws cirle on image, center_coordinates, radius, color(BGR), thickness)
            cv2.imshow("Image", img)


def init_cam(num=0):
    return cv2.VideoCapture(num)


def close_cam(vid):
    vid.release()


def get_frame(vid):
    if DEBUG_CAM_IS_IMG:
        return _img
    ret, frame = vid.read()
    return frame


def get_cam_size(vid):
    frame = get_frame(vid)
    height, width, _ = frame.shape
    return width, height


def get_face_mesh_from_cam(vid, get_all_points=False):
    frame = get_frame(vid)
    res = get_face_mash(frame, get_all_points=get_all_points)
    return res


def draw_points_face(vid):
    ret, frame = vid.read()
    height, width, _ = frame.shape
    result = get_face_points(frame)
    mp_drawing = mp.solutions.drawing_utils
    mp_drawing_styles = mp.solutions.drawing_styles

    if result.multi_face_landmarks:
        mfl0 = list(result.multi_face_landmarks)[0]

        for i, p in enumerate(mfl0.landmark):
            pos = int(p.x * width), int(p.y * height)
            cv2.circle(frame, pos, 1, (0, 0, 0), 2)
            cv2.putText(frame, str(i), pos, 0, 0.3, (0, 200, 0))
        # mp_drawing.draw_landmarks(
        #     image=frame,
        #     landmark_list=mfl0,
        #     connections=mp_face_mesh.FACEMESH_IRISES,
        #     connection_drawing_spec=mp_drawing_styles
        #     .get_default_face_mesh_iris_connections_style())

    cv2.imshow("Frame", frame)


if __name__ == '__main__':
    DEBUG_CAM_IS_IMG = True
    TYP = 1
    t = time.time()
    if TYP == 0:
        cam = init_cam()
        while 1:
            _, img = cam.read()
            res = get_face_mesh_from_cam(cam)
            # draw_contours(img, res)
            s = time.time() - t
            print(s, 1 / s)
            t = time.time()
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
        cv2.destroyAllWindows()
    elif TYP == 1:
        cam = init_cam()
        while 1:
            draw_points_face(cam)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
        cv2.destroyAllWindows()
    elif TYP == 2:
        cam = init_cam()
        mp_drawing = mp.solutions.drawing_utils
        while 1:
            frame = get_frame(cam)
            result = get_face_points(frame)
            if result.multi_face_landmarks:
                mfl0 = list(result.multi_face_landmarks)[0]
                mp_drawing.draw_landmarks(
                    image=frame,
                    landmark_list=mfl0,
                    connections=mp_face_mesh.FACEMESH_TESSELATION, )
            cv2.imshow("Frame", frame)

            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
        cv2.destroyAllWindows()
    else:
        image = cv2.imread("img.jpg")
        res = get_face_mash(image)
        draw_contours(image, res)
        while 1:
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
        cv2.destroyAllWindows()
