import cv2
import mediapipe as mp
from mediapipe.python.solutions.face_mesh_connections import FACEMESH_LIPS, FACEMESH_LEFT_EYE, FACEMESH_LEFT_EYEBROW, \
    FACEMESH_RIGHT_EYE, FACEMESH_RIGHT_EYEBROW, FACEMESH_FACE_OVAL, FACEMESH_NOSE

# Face Mesh
mp_draw = mp.solutions.drawing_utils
mp_face_mesh = mp.solutions.face_mesh
face_mesh = mp_face_mesh.FaceMesh()


def get_face_mash(image):
    height, width, _ = image.shape
    rgb_image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

    result = face_mesh.process(rgb_image)
    contours = (FACEMESH_LIPS, FACEMESH_LEFT_EYE, FACEMESH_LEFT_EYEBROW, FACEMESH_RIGHT_EYE,
                FACEMESH_RIGHT_EYEBROW, FACEMESH_FACE_OVAL, FACEMESH_NOSE )
    if result.multi_face_landmarks:
        mfl0 = list(result.multi_face_landmarks)[0]
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


if __name__ == '__main__':
    # if 1:
    #     cam = init_cam()
    #     while 1:
    #         _, img = cam.read()
    #         res = get_face_mesh_from_cam(cam)
    #         draw_contours(img, res)
    #         if cv2.waitKey(1) & 0xFF == ord('q'):
    #             break
    #     cv2.destroyAllWindows()
    # else:
        image = cv2.imread("img.jpg")
        res = get_face_mash(image)
        draw_contours(image, res)
        while 1:
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
        cv2.destroyAllWindows()
