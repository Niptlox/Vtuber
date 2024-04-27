from typing import Tuple

from pygame import Vector3, Vector2

from face import Face
from numpy import arccos, pi

from face_mesh_connections import NUM_LEFT_EYE, NUM_RIGHT_EYE, NUM_CENTER

DEFAULT_DIST_TO_FACE = 50
FACE_COF = 20


def add_ddtf(v):
    global DEFAULT_DIST_TO_FACE
    DEFAULT_DIST_TO_FACE += v
    print("DEFAULT_DIST_TO_FACE", DEFAULT_DIST_TO_FACE)


def face2pos(all_points, base_point, base_eyes, in_degrees=True):
    cf = get_face_cof(all_points, base_eyes)
    z = DEFAULT_DIST_TO_FACE / cf
    # print(int(z), cf)
    base = (Vector3(all_points[0].x, all_points[0].y, 0) - base_point) * -FACE_COF
    base.z = -z
    vec = base.normalize()
    horizontal_angle = arccos(vec.y)
    vertical_angle = arccos(vec.x)
    # print(horizontal_angle * 180 / pi, vec)
    if in_degrees:
        return horizontal_angle * 180 / pi, vertical_angle * 180 / pi
    return (horizontal_angle, vertical_angle), base, cf


def get_face_cof(all_points, base_eyes):
    return get_eyes_dist(all_points) / base_eyes


def get_dist(p1, p2):
    return Vector3(p1.x - p2.x, p1.y - p2.y, p1.z - p2.z).length()


def get_eyes_dist(all_points):
    p1, p2 = (all_points[NUM_LEFT_EYE], all_points[NUM_RIGHT_EYE])
    return Vector3(p1.x - p2.x, p1.y - p2.y, (p1.z - p2.z) * 1.1).length()


def get_base(all_points) -> Tuple[Vector3, float]:
    # return Vector3(0.5,0.5,0.5)
    return Vector3(all_points[NUM_CENTER].x, all_points[NUM_CENTER].y, 0.5), get_eyes_dist(all_points)
