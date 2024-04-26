from cmath import pi
from typing import Tuple

import numpy as np
from pygame import Vector2

import pygame as pg

from One3D import Producer, Camera, Scene3D, create_cube, BLACK, Vector3, OBJECT_FLAG_MAP, Object3d, create_normal, \
    convert_faces_to_lines, WHITE, RED, VertexPoint, load_object_from_fileobj
from face import Face
from face_mesh import get_face_points, get_frame, init_cam, get_face
from face_mesh_connections import FACEMESH_TESSELATION, FACEMESH_SURFACES, LEFT_IRIS_SURFACES, RIGHT_IRIS_SURFACES
from face_position import get_base_point, face2pos
from main import draw_face

screen = pg.display.set_mode((780, 420))
pi2 = pi / 2


class WindowCamera3D(Camera):
    def __init__(self, owner, scene, screen, position, rotation, background=(10, 10, 10), a=0):
        super().__init__(owner, scene, screen, position, rotation, background=background)
        self.eye_position = Vector3(0, 0, 0)
        self.window_position = Vector3(0, 0, a)

    def calc_point(self, global_position) -> Tuple[Tuple[float, float], float, bool]:
        position_from_camera = global_position - self.global_position
        vec_at_center = self.get_matrix_rotation() * position_from_camera
        vec_at_eye = vec_at_center - self.eye_position
        dist = vec_at_eye[2]
        if dist == 0:
            dist = 1e-9
        eye_at_win = self.eye_position - self.window_position
        focus = self.window_position.z - self.eye_position.z
        x = (focus * vec_at_eye[0] / dist + eye_at_win.x) + self.half_w
        y = self.half_h - (focus * vec_at_eye[1] / dist + eye_at_win.y)
        is_visible = self.surface_rect.collidepoint((x, y)) and dist > 0
        return (x, y), dist, is_visible


def vec(point):
    return pg.Vector3(point.x, point.y, point.z)


def convert_points(points):
    cof = 30
    return [((p.x - 0.5) * -cof, (p.y - 0.5) * -cof, (p.z - 0.5) * cof) for p in points]


colors = [WHITE] * len(FACEMESH_SURFACES) + [RED] * (len(LEFT_IRIS_SURFACES) * 2)


def draw_face3d(scene3d: Scene3D, face: Face, objects=None):
    if not face.all_points:
        return
    surfaces = FACEMESH_SURFACES + RIGHT_IRIS_SURFACES + LEFT_IRIS_SURFACES
    points = convert_points(face.all_points)
    normals = [create_normal(vec(face.all_points[p1]), vec(face.all_points[p2]), vec(face.all_points[p3])) * 100
               for p1, p2, p3 in surfaces]
    normals = [v if v.z < 0 else -v for v in normals]
    face3d = Object3d(None, (0, 0, 0), points, FACEMESH_TESSELATION, surfaces, normals=normals, colors=colors)

    # points_left = convert_points([face.all_points[i] for i in LEFT_IRIS_SURFACES])
    # edges = convert_faces_to_lines(FACEMESH_SURFACES)

    scene3d.static = [face3d]
    if objects:
        scene3d.static += objects
    # face3d.show(camera, None)


def main():
    w, h = 1200, 1000
    screen = pg.display.set_mode((w, h), flags=pg.RESIZABLE)
    running = True
    obj = create_cube(None, (0, -5, 10), 13)
    # obj = load_object_from_fileobj(None, (0, 10, 0), "bedroom0.obj", scale=1)
    obj = load_object_from_fileobj(None, (0, -118, 15), "bedroom1.obj", scale=10)
    # obj = VertexPoint(None, (0, -5, 0))
    objects = [obj]
    scene3d = Scene3D()
    scene3d.add_static(obj)
    camera3d = Camera(None, scene3d, screen, Vector3(0, 0, -15), Vector3(0, 0, 0), background=(10, 10, 10))
    camera3d_ = WindowCamera3D(None, scene3d, screen, Vector3(0, 0, 0), Vector3(0, 0, 0), background=None, a=0)

    producer = Producer()
    # producer.add_camera(camera3d)
    producer.add_camera(camera3d_)

    cam = init_cam(0)
    base_point = get_base_point(get_face_points(get_frame(cam)))

    vec0 = pg.Vector2(100, 100)
    vec1 = pg.Vector2(0, 50)

    while running:
        [exit() for event in pg.event.get(pg.QUIT)]
        screen.fill(BLACK)
        face = get_face(cam, auto_hide_iris=False)
        if face.all_points:
            angle, pos0 = face2pos(face.all_points, base_point, in_degrees=False)
            # obj.set_rotation(Vector3(((angle[0] - pi2), -(angle[1] - pi2), 0)))
            # print(x_angle, -(x_angle - pi / 2))
            # a = [p.z for p in face.all_points]
            # print(sum(a)/len(a), min(a), max(a))


        # draw_face3d(scene3d, face, objects)
        camera3d_.eye_position = Vector3(-pos0.x*100, -pos0.y*100, camera3d_.eye_position.z)
        print(camera3d_.eye_position)
        producer.show()
        # draw_face(screen, face)

        # p = Vector2(300, 500)
        # v = p + pg.math.Vector2(0, 100).rotate_rad(x_angle - pi2)
        # pg.draw.line(screen, "green", p, v)
        # p = Vector2(800, 500)
        # v = p + pg.math.Vector2(0, 100).rotate_rad(y_angle - pi2)
        # pg.draw.line(screen, "green", p, v)

        #  ================ DOT ==================
        # pg.draw.line(screen, "red", vec0, vec0+vec1)
        # vec2 = pg.Vector2(*pg.mouse.get_pos()) - vec0
        # pg.draw.line(screen, "yellow", vec0, vec0 + vec2)
        # print(vec1.normalize().dot(vec2.normalize()))
        #  ============== END DOT ================

        pg.display.flip()


if __name__ == '__main__':
    main()
