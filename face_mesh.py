import cv2
import mediapipe as mp
from mediapipe.python.solutions.face_mesh_connections import FACEMESH_LIPS, FACEMESH_LEFT_EYE, FACEMESH_LEFT_EYEBROW, \
    FACEMESH_RIGHT_EYE, FACEMESH_RIGHT_EYEBROW, FACEMESH_FACE_OVAL, FACEMESH_NOSE, FACEMESH_RIGHT_IRIS, \
    FACEMESH_LEFT_IRIS, FACEMESH_IRISES

# Face Mesh
mp_draw = mp.solutions.drawing_utils
mp_face_mesh = mp.solutions.face_mesh
face_mesh = mp_face_mesh.FaceMesh(static_image_mode=False,
                                  max_num_faces=1,
                                  refine_landmarks=True,
                                  min_detection_confidence=0.5)

LIP_TOP = frozenset([(61, 185), (185, 40), (40, 39), (39, 37),
                     (37, 0), (0, 267), (267, 269), (269, 270), (270, 409), (409, 291),

                     (78, 191), (191, 80), (80, 81), (81, 82),
                     (82, 13), (13, 312), (312, 311), (311, 310),
                     (310, 415), (415, 308),
                     ])

LIP_BOTTOM = frozenset([(61, 146), (146, 91), (91, 181), (181, 84), (84, 17),
                        (17, 314), (314, 405), (405, 321), (321, 375), (375, 291),


                        (78, 95), (95, 88), (88, 178), (178, 87), (87, 14),
                        (14, 317), (317, 402), (402, 318), (318, 324), (324, 308),

                        ])


def get_face_points(image):
    height, width, _ = image.shape
    rgb_image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    return face_mesh.process(rgb_image)


contours = (LIP_TOP, LIP_BOTTOM, FACEMESH_LEFT_EYE, FACEMESH_RIGHT_EYE, FACEMESH_LEFT_EYEBROW,
            FACEMESH_RIGHT_EYEBROW, FACEMESH_FACE_OVAL, FACEMESH_NOSE, FACEMESH_LEFT_IRIS, FACEMESH_RIGHT_IRIS)


def get_face_mash(image):
    result = get_face_points(image)
    if result.multi_face_landmarks:
        mfl0 = list(result.multi_face_landmarks)[0]
        # print(len(list(mfl0.landmark)))
        res = [[(mfl0.landmark[i1], mfl0.landmark[i2]) for i1, i2 in fig] for fig in contours]
        return res
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


def get_cam_size(vid):
    ret, frame = vid.read()
    # frame = cv2.imread("img.jpg")
    height, width, _ = frame.shape
    return width, height


def get_face_mesh_from_cam(vid):
    ret, frame = vid.read()
    # frame = cv2.imread("img.jpg")
    res = get_face_mash(frame)
    return res


def draw_points_face(vid):
    ret, frame = vid.read()
    height, width, _ = frame.shape
    result = get_face_points(frame)
    mp_drawing = mp.solutions.drawing_utils
    mp_drawing_styles = mp.solutions.drawing_styles

    if result.multi_face_landmarks:
        mfl0 = list(result.multi_face_landmarks)[0]
        for p in mfl0.landmark:
            cv2.circle(frame, (int(p.x * width), int(p.y * height)), 1, (0, 0, 0), 2)

        # mp_drawing.draw_landmarks(
        #     image=frame,
        #     landmark_list=mfl0,
        #     connections=mp_face_mesh.FACEMESH_IRISES,
        #     connection_drawing_spec=mp_drawing_styles
        #     .get_default_face_mesh_iris_connections_style())

    cv2.imshow("Frame", frame)


if __name__ == '__main__':
    if 0:
        cam = init_cam()
        while 1:
            _, img = cam.read()
            res = get_face_mesh_from_cam(cam)
            draw_contours(img, res)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
        cv2.destroyAllWindows()
    elif 2:
        cam = init_cam()
        while 1:
            draw_points_face(cam)
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
