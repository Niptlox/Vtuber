from cmath import pi

import numpy as np
from pygame import Vector2

import pygame as pg

from One3D import Producer, Camera, Scene3D, create_cube, BLACK, Vector3, OBJECT_FLAG_MAP, Object3d
from face_mesh import get_face_points, get_frame, init_cam, get_face
from face_mesh_connections import FACEMESH_TESSELATION
from face_position import get_base_point, face2angle
from main import draw_face

screen = pg.display.set_mode((780, 420))
pi2 = pi / 2


def draw_face3d(camera, face):
    if not face.all_points:
        return
    cof = 30
    points = [((p.x-0.5)*-cof, (p.y-0.5)*-cof, (p.z-0.5)*cof) for p in face.all_points]
    # print(points)
    face3d = Object3d(None, (0, 0, 0), points, FACEMESH_TESSELATION)
    face3d.show(camera, None)


def main():
    screen = pg.display.set_mode((1200, 1000), flags=pg.RESIZABLE)
    running = True
    obj = create_cube(None, (0, -5, 0), 13)
    scene3d = Scene3D()
    # scene3d.add_static(obj)
    camera3d = Camera(scene3d, scene3d, screen, (0, 0, -50), (0, 0, 0), background=(10, 10, 10))
    producer = Producer()
    producer.add_camera(camera3d)

    cam = init_cam(0)
    base_point = get_base_point(get_face_points(get_frame(cam)))

    while running:
        [exit() for event in pg.event.get(pg.QUIT)]
        screen.fill(BLACK)
        face = get_face(cam, auto_hide_iris=False)
        if face.all_points:
            x_angle, y_angle = face2angle(face.all_points, base_point, in_degrees=False)
            # print(x_angle, -(x_angle - pi / 2))

        obj.set_rotation(Vector3(((x_angle - pi2), -(y_angle - pi2), 0)))
        producer.show()
        draw_face3d(camera3d, face)
        # draw_face(screen, face)

        p = Vector2(300, 500)
        v = p + pg.math.Vector2(0, 100).rotate_rad(x_angle - pi2)
        pg.draw.line(screen, "green", p, v)
        p = Vector2(800, 500)
        v = p + pg.math.Vector2(0, 100).rotate_rad(y_angle - pi2)
        pg.draw.line(screen, "green", p, v)

        pg.display.flip()


if __name__ == '__main__':
    main()
