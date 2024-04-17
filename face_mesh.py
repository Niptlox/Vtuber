import time
from random import shuffle
from typing import NamedTuple, List

import cv2
import mediapipe as mp

from face import TILT_LEFT, TILT_RIGHT, NO_TILT, FaceState, Face
from face_mesh_connections import NUM_TOP, NUM_BOTTOM, NUM_RIGHT_EYE_TOP, NUM_RIGHT_EYE_BOTTOM, NUM_LEFT_EYE_BOTTOM, \
    NUM_LEFT_EYE_TOP, NUP_LIP_BOTTOM_TOP, NUP_LIP_TOP_BOTTOM
from face_position import face2angle, get_base_point

ABRAKADABRA = False

if ABRAKADABRA:
    from mediapipe.python.solutions.face_mesh_connections import FACEMESH_LEFT_EYE, FACEMESH_LEFT_EYEBROW, \
        FACEMESH_RIGHT_EYE, FACEMESH_RIGHT_EYEBROW, FACEMESH_FACE_OVAL, FACEMESH_NOSE, FACEMESH_RIGHT_IRIS, \
        FACEMESH_LEFT_IRIS, FACEMESH_LIPS
    from face_mesh_connections import _LIP_TOP as LIP_TOP, _LIP_BOTTOM as LIP_BOTTOM
else:
    from face_mesh_connections import FACEMESH_LEFT_EYE, FACEMESH_LEFT_EYEBROW, \
        FACEMESH_RIGHT_EYE, FACEMESH_RIGHT_EYEBROW, FACEMESH_FACE_OVAL, FACEMESH_NOSE, FACEMESH_RIGHT_IRIS, \
        FACEMESH_LEFT_IRIS, LIP_TOP, LIP_BOTTOM, FACEMESH_LIPS
CONTOURS = [FACEMESH_FACE_OVAL, LIP_TOP, LIP_BOTTOM, FACEMESH_LEFT_EYE, FACEMESH_RIGHT_EYE, FACEMESH_LEFT_EYEBROW,
            FACEMESH_RIGHT_EYEBROW, FACEMESH_NOSE, FACEMESH_LEFT_IRIS, FACEMESH_RIGHT_IRIS]

# Face Mesh
mp_draw = mp.solutions.drawing_utils
mp_face_mesh = mp.solutions.face_mesh
face_mesh = mp_face_mesh.FaceMesh(static_image_mode=False, max_num_faces=1,
                                  refine_landmarks=True, min_detection_confidence=0.5)
_img = cv2.imread("img.jpg")
DEBUG_CAM_IS_IMG = False


def get_face_points(image) -> list:
    # height, width, _ = image.shape
    result = face_mesh.process(cv2.cvtColor(image, cv2.COLOR_BGR2RGB))
    if result.multi_face_landmarks:
        points = result.multi_face_landmarks[0].landmark
        return list(points)
    return []


def shuffle_contours():
    global CONTOURS
    for x in CONTOURS:
        shuffle(x)


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
    points = get_face_points(image)
    if points:
        res = points2counters(points)
        if get_all_points:
            return res, points
        return res
    if get_all_points:
        return [[]], None
    return [[]]


def points2counters(points):
    return [[[points[i1], points[i2]] for i1, i2 in fig if points[i1] is not None] for fig in CONTOURS]


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
        return _img.copy()
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


def get_face(vid, auto_hide_iris=True) -> Face:
    frame = get_frame(vid)
    points = get_face_points(frame)
    state = get_face_state(points)
    contours = []
    if points:
        if auto_hide_iris:
            if state.left_eye_closed:
                points[474] = points[475] = points[476] = points[477] = None
            else:
                # h1 = points[475].y - points[477].y
                points[475].y = max(points[NUM_LEFT_EYE_TOP].y, points[475].y)
                points[477].y = min(points[NUM_LEFT_EYE_BOTTOM].y, points[477].y)
                # h2 = points[475].y - points[477].y
            if state.right_eye_closed:
                points[469] = points[470] = points[471] = points[472] = None
            else:
                points[470].y = max(points[NUM_RIGHT_EYE_TOP].y, points[470].y)
                points[472].y = min(points[NUM_RIGHT_EYE_BOTTOM].y, points[472].y)
        contours = points2counters(points)
    face = Face(contours=contours, all_points=points, state=state, image=frame)
    # print(state)
    return face


def get_face_state(all_points):
    if not all_points:
        return None
    ax = all_points[NUM_TOP].x - all_points[NUM_BOTTOM].x
    offset = 0.09
    if ax > offset:
        tilt = TILT_RIGHT
    elif ax < -offset:
        tilt = TILT_LEFT
    else:
        tilt = NO_TILT
    # tilt = ax
    eye_thr = 0.011
    ay = all_points[NUM_RIGHT_EYE_BOTTOM].y - all_points[NUM_RIGHT_EYE_TOP].y
    right_eye_closed = ay < eye_thr
    right_eye_cof = 0.005 / (ay - eye_thr) if eye_thr <= ay <= eye_thr + 0.005 else 1
    ay = all_points[NUM_LEFT_EYE_BOTTOM].y - all_points[NUM_LEFT_EYE_TOP].y
    left_eye_closed = ay < eye_thr
    left_eye_cof = 0.005 / (ay - eye_thr) if eye_thr <= ay <= eye_thr + 0.005 else 1
    eyes_closed = right_eye_closed and left_eye_closed
    ay = all_points[NUP_LIP_BOTTOM_TOP].y - all_points[NUP_LIP_TOP_BOTTOM].y
    mouth_closed = ay < 0.001
    return FaceState(tilt=tilt, left_eye_closed=left_eye_closed, right_eye_closed=right_eye_closed,
                     left_eye_cof=left_eye_cof, right_eye_cof=right_eye_cof,
                     eyes_closed=eyes_closed, mouth_closed=mouth_closed)


def draw_points_face(vid):
    frame = get_frame(vid)
    height, width, _ = frame.shape
    all_points = get_face_points(frame)
    # mp_drawing = mp.solutions.drawing_utils
    # mp_drawing_styles = mp.solutions.drawing_styles
    arrrrr = {i for p in FACEMESH_RIGHT_IRIS for i in p}
    if all_points:
        for i, p in enumerate(all_points):
            if i in arrrrr:
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
    DEBUG_CAM_IS_IMG = 0
    TYP = 2
    t = time.time()
    cam = init_cam(0)
    if TYP == 0:
        while 1:
            _, img = cam.read()
            res = get_face_mesh_from_cam(cam)
            draw_contours(img, res)
            s = time.time() - t
            print(s, 1 / s)
            t = time.time()
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
        cv2.destroyAllWindows()
    elif TYP == 1:
        while 1:
            draw_points_face(cam)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
        cv2.destroyAllWindows()
    elif TYP == 2:

        mp_drawing = mp.solutions.drawing_utils
        base_point = get_base_point(get_face_points(get_frame(cam)))
        while 1:
            frame = get_frame(cam)
            res = face_mesh.process(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
            # all_points = get_face_points(frame)
            if res.multi_face_landmarks:
                mfl0 = res.multi_face_landmarks[0]
                mp_drawing.draw_landmarks(
                    image=frame,
                    landmark_list=mfl0,
                    connections=mp_face_mesh.FACEMESH_TESSELATION, )
                print(face2angle(mfl0.landmark, base_point))
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
