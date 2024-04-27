import math
from cmath import pi
from typing import Tuple

import numpy as np
from pygame import Vector2

import pygame as pg

from One3D import Producer, Camera, Scene3D, create_cube, BLACK, Vector3, OBJECT_FLAG_MAP, Object3d, create_normal, \
    convert_faces_to_lines, WHITE, RED, VertexPoint, load_object_from_fileobj, GREEN, BLUE
from face import Face
from face_mesh import get_face_points, get_frame, init_cam, get_face
from face_mesh_connections import FACEMESH_TESSELATION, FACEMESH_SURFACES, LEFT_IRIS_SURFACES, RIGHT_IRIS_SURFACES
from face_position import face2pos, get_base, get_eyes_dist
from main import draw_face

# screen = pg.display.set_mode((780, 420))
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

    def get_window_pos(self):
        return self.global_position + self.window_position


def vec(point):
    return pg.Vector3(point.x, point.y, point.z)


def convert_points(points, point0, cof=30):
    p0x, p0y, p0z = points[0].x, points[0].y, points[0].z
    return [(point0+(p.x-p0x, p.y-p0y, p.z-p0z))*-cof for p in points]


colors = [BLUE] * len(FACEMESH_SURFACES) + [RED] * (len(LEFT_IRIS_SURFACES) * 2)


def draw_face3d(scene3d: Scene3D, position, face: Face, point0, face_cof, objects):
    if not face.all_points:
        return
    surfaces = FACEMESH_SURFACES + RIGHT_IRIS_SURFACES + LEFT_IRIS_SURFACES
    points = [p + position for p in convert_points(face.all_points, point0, cof=30/face_cof)]
    normals = [create_normal(vec(face.all_points[p1]), vec(face.all_points[p2]), vec(face.all_points[p3])) * 500
               for p1, p2, p3 in surfaces]
    normals = [v if v.z > 0 else -v for v in normals]
    surfaces += surfaces
    normals += [-v for v in normals]
    face3d = Object3d(None, (0, 0, 0), points, FACEMESH_TESSELATION, surfaces, normals=normals, colors=colors)

    # points_left = convert_points([face.all_points[i] for i in LEFT_IRIS_SURFACES])
    # edges = convert_faces_to_lines(FACEMESH_SURFACES)

    scene3d.static = [face3d]
    if objects:
        scene3d.static += objects

    # face3d.show(camera, None)


def update_keys(camera, elapsed_time):
    keys = pg.key.get_pressed()
    speed = 0.2 * elapsed_time
    rot_speed = 0.002 * elapsed_time
    # поворот объекта
    rx, ry, rz = 0, 0, 0
    if keys[pg.K_LEFT]:
        ry = 1
    elif keys[pg.K_RIGHT]:
        ry = -1
    if keys[pg.K_UP]:
        rx = -1
    elif keys[pg.K_DOWN]:
        rx = 1
    camera.set_rotation(camera.rotation + Vector3(rx, ry, rz) * rot_speed)
    vec_speed = Vector3(0, 0, 0)
    # смещение
    ry = camera.rotation.y
    if keys[pg.K_w]:
        vec_speed = Vector3(-math.sin(ry), 0, math.cos(ry))
    elif keys[pg.K_s]:
        vec_speed = -Vector3(-math.sin(ry), 0, math.cos(ry))
    if keys[pg.K_a]:
        vec_speed += -Vector3(math.cos(ry), 0, math.sin(ry))
    elif keys[pg.K_d]:
        vec_speed += Vector3(math.cos(ry), 0, math.sin(ry))
    if keys[pg.K_q]:
        vec_speed += Vector3(0, -1, 0)
    if keys[pg.K_e]:
        vec_speed += Vector3(0, 1, 0)
    camera.position = camera.position + vec_speed * speed
    if keys[pg.K_0]:
        camera.position = start_position


start_position = Vector3(0, 118, 0)



def main():
    pg.init()
    W, H = pg.display.Info().current_w, pg.display.Info().current_h
    print(W, H)
    screen = pg.display.set_mode((W, H), flags=pg.RESIZABLE)
    running = True

    # obj = load_object_from_fileobj(None, (0, 10, 0), "bedroom0.obj", scale=1)
    obj = load_object_from_fileobj(None, (0, 0, 15), "bedroom1.obj", scale=1)
    tab = load_object_from_fileobj(None, (0, 0, 15), "table.obj", scale=1, color=RED)
    # obj = VertexPoint(None, (0, -5, 0))
    cube_w = create_cube(None, Vector3(0, 0, 0), 1, color=GREEN)
    objects = [obj, tab, cube_w]
    scene3d = Scene3D()
    scene3d.add_static(objects)
    camera3d = Camera(None, scene3d, screen, Vector3(start_position), Vector3(0, 0, 0), background=(10, 10, 10))
    camera3d_ = WindowCamera3D(None, scene3d, screen, Vector3(start_position), Vector3(0, 0, 0), background=None, a=0)
    obj = create_cube(camera3d_, (0, -0, 0), 10, color=GREEN)

    producer = Producer()
    producer.add_camera(camera3d)
    # producer.add_camera(camera3d_)

    cam = init_cam(0)
    base_point, base_dist_eyes = get_base(get_face_points(get_frame(cam)))

    vec0 = pg.Vector2(100, 100)
    vec1 = pg.Vector2(0, 50)

    clock = pg.time.Clock()

    while running:
        elaps = clock.tick(60)
        # print(clock.get_fps())
        update_keys(camera3d, elaps)
        [exit() for event in pg.event.get(pg.QUIT)]

        screen.fill(BLACK)
        face = get_face(cam, auto_hide_iris=False)
        if face.all_points:
            angle, pos0, face_cof = face2pos(face.all_points, base_point, base_dist_eyes, in_degrees=False)
            eyes_dist = get_eyes_dist(face.all_points)
            print("e", pos0)
            # obj.set_rotation(Vector3(((angle[0] - pi2), -(angle[1] - pi2), 0)))
            # print(x_angle, -(x_angle - pi / 2))
            # a = [p.z for p in face.all_points]
            # print(sum(a)/len(a), min(a), max(a))
            draw_face3d(scene3d, pos0 + start_position, face, pos0, face_cof, objects)
        camera3d_.eye_position = Vector3(-pos0.x * 100, -pos0.y * 100, camera3d_.eye_position.z)
        cube_w.position = camera3d_.get_window_pos()
        # print(camera3d_.eye_position)
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
