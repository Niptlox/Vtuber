from pygame import Vector3

from face import Face
from numpy import arccos, pi


def face2pos(all_points, base_point, in_degrees=True):
    base = (Vector3(all_points[0].x, all_points[0].y, all_points[0].z) - base_point)
    vec = base.normalize()
    horizontal_angle = arccos(vec.y)
    vertical_angle = arccos(vec.x)
    # print(horizontal_angle * 180 / pi, vec)
    if in_degrees:
        return horizontal_angle * 180 / pi, vertical_angle * 180 / pi

    return (horizontal_angle, vertical_angle), base


def get_base_point(all_points) -> Vector3:
    # return Vector3(0.5,0.5,0.5)
    return Vector3(all_points[0].x, all_points[0].y, 0.5)
