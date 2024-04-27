import math
from cmath import pi
from typing import Tuple, List

import numpy as np
from pygame import Vector2

import pygame as pg

from One3D import Producer, Camera, Scene3D, create_cube, BLACK, Vector3, OBJECT_FLAG_MAP, Object3d, create_normal, \
    convert_faces_to_lines, WHITE, RED, VertexPoint, load_object_from_fileobj, GREEN, BLUE, create_sys_coord
from face import Face
from face_mesh import get_face_points, get_frame, init_cam, get_face
from face_mesh_connections import FACEMESH_TESSELATION, FACEMESH_SURFACES, LEFT_IRIS_SURFACES, RIGHT_IRIS_SURFACES, \
    NUM_CENTER
from face_position import face2pos, get_base, get_eyes_dist, DEFAULT_DIST_TO_FACE, add_ddtf, FACE_COF
from main import draw_face

# screen = pg.display.set_mode((780, 420))
pi2 = pi / 2
DEFAULT_BETWEEN_EYES = 0
TYP = 1


class WindowCamera3D(Camera):
    def __init__(self, owner, scene, screen, position, rotation, sys_coord, background=(10, 10, 10)):
        super().__init__(owner, scene, screen, position, rotation, background=background)
        self.sys_coord = sys_coord
        self.eye_position = Vector3(0, 0, 0)

    def calc_point(self, global_position) -> Tuple[Tuple[float, float], float, bool]:
        p = global_position
        f = abs(self.sys_coord.position.z - self.eye_position.z)
        d = abs(p.z - self.eye_position.z)
        if d == 0:
            d = 1e-9
        k = f / d
        vec = p - self.eye_position
        np = vec * k + self.eye_position
        # =====
        jx, jy = np.x - self.sys_coord.position.x, np.y - self.sys_coord.position.y
        x, y = jx / self.sys_coord.x_length * self.width, self.height - jy / self.sys_coord.y_length * self.height
        dist = p.z - self.sys_coord.position.z
        is_visible = dist > 0 and self.surface_rect.collidepoint(x, y)
        return (x, y), d, is_visible

    def get_window_pos(self):
        return self.global_position + self.window_position


def vec(point):
    return pg.Vector3(point.x, point.y, point.z)


def convert_points(points, point0, cof=30):
    p0x, p0y, p0z = points[NUM_CENTER].x, points[NUM_CENTER].y, points[NUM_CENTER].z
    return [point0 + (Vector3(p.x - p0x, p.y - p0y, p.z - p0z) * -cof) for p in points]


colors = [BLUE] * len(FACEMESH_SURFACES) + [RED] * (len(LEFT_IRIS_SURFACES) * 2)

DUBL = 1


def draw_face3d(scene3d: Scene3D, position, face: Face, point0, face_cof, objects):
    if not face.all_points:
        return
    surfaces = FACEMESH_SURFACES + RIGHT_IRIS_SURFACES + LEFT_IRIS_SURFACES
    points = [p + position for p in convert_points(face.all_points, point0, cof=FACE_COF / face_cof)]
    normals = [create_normal(vec(face.all_points[p1]), vec(face.all_points[p2]), vec(face.all_points[p3])) * 500
               for p1, p2, p3 in surfaces]
    normals = [v if v.z > 0 else -v for v in normals]
    if DUBL:
        surfaces += surfaces
        normals += [-v for v in normals]
    face3d = Object3d(None, (0, 0, 0), points, FACEMESH_TESSELATION, surfaces, normals=normals, colors=colors)

    # points_left = convert_points([face.all_points[i] for i in LEFT_IRIS_SURFACES])
    # edges = convert_faces_to_lines(FACEMESH_SURFACES)

    scene3d.static = [face3d]
    if objects:
        scene3d.static += objects

    return points[NUM_CENTER]

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
    global TYP
    if keys[pg.K_1]:
        set_typ_view(1)
    if keys[pg.K_2]:
        set_typ_view(2)
    camera.position = camera.position + vec_speed * speed
    if keys[pg.K_0]:
        camera.position = start_position
        camera.set_rotation(Vector3(0, 0, 0))


def set_typ_view(typ):
    global TYP
    TYP = typ
    if TYP == 1:
        camera3d_.active = False
        camera3d.active = True
    else:
        camera3d_.active = True
        camera3d.active = False


start_position = Vector3(0, 118, 0)


def draw_lines(camera: Camera, points1, points2, color=GREEN):
    for p1 in points1:
        if isinstance(p1, VertexPoint):
            p1 = p1.position
        for p2 in points2:
            r1, r2 = camera.calc_point(Vector3(p1)), camera.calc_point(p2.global_position)
            if r1[2] and r2[2]:
                pg.draw.line(camera.surface, color, r1[0], r2[0], 1)


def processing_window(camera, sys_coord: "System coord obj", point0: Vector3, objects: List[Object3d], color=BLUE):
    for obj in objects:
        for p_ in obj.points:
            p = p_.global_position
            f = abs(sys_coord.position.z - point0.z)
            d = abs(p.z - point0.z)
            k = f / d
            vec = p - point0
            np = vec * k + point0
            res_np = camera.calc_point(np)
            if res_np[2]:
                if sys_coord.position.x <= np.x <= (sys_coord.position.x + sys_coord.x_length) and \
                        sys_coord.position.y <= np.y <= (sys_coord.position.y + sys_coord.y_length):
                    pg.draw.circle(camera.surface, color, res_np[0], 3)
                # else:
                #     pg.draw.circle(camera.surface, RED, res_np[0], 3)


def main():
    global camera3d, camera3d_
    pg.init()
    W, H = pg.display.Info().current_w, pg.display.Info().current_h
    print(W, H)
    screen = pg.display.set_mode((W, H), flags=pg.RESIZABLE)
    running = True

    # obj = load_object_from_fileobj(None, (0, 10, 0), "bedroom0.obj", scale=1)
    room = load_object_from_fileobj(None, (0, 0, 15), "bedroom.obj", scale=1)
    tab = load_object_from_fileobj(None, (0, 0, 15), "table.obj", scale=1, color=RED)
    # obj = VertexPoint(None, (0, -5, 0))
    cube_w = create_cube(None, Vector3(0, 0, 0), 10, color=GREEN)
    sys3d = create_sys_coord(None, Vector3(-30, 100, 15), (60, 34, 10), 1)
    scene3d = Scene3D()
    scene3d.add_static([room, tab, sys3d, cube_w])
    objects = list(scene3d.static)
    camera3d = Camera(None, scene3d, screen, Vector3(start_position), Vector3(0, 0, 0), background=(10, 10, 10))
    camera3d_ = WindowCamera3D(None, scene3d, screen, Vector3(start_position), Vector3(0, 0, 0), sys3d, background=None)
    # obj = create_cube(camera3d_, (0, -0, 0), 10, color=GREEN)

    producer = Producer()
    producer.add_camera(camera3d)
    producer.add_camera(camera3d_)
    set_typ_view(TYP)
    cam = init_cam(0)
    base_point, base_dist_eyes = get_base(get_face_points(get_frame(cam)))
    if DEFAULT_BETWEEN_EYES:
        base_dist_eyes = DEFAULT_BETWEEN_EYES
    vec0 = pg.Vector2(100, 100)
    vec1 = pg.Vector2(0, 50)

    clock = pg.time.Clock()

    while running:
        screen.fill((0, 0, 0))
        elaps = clock.tick(60)
        # print(clock.get_fps())
        update_keys(camera3d, elaps)
        [exit() for event in pg.event.get(pg.QUIT)]

        screen.fill(BLACK)
        face = get_face(cam, auto_hide_iris=False)
        if face.all_points:
            angle, pos0, face_cof = face2pos(face.all_points, base_point, base_dist_eyes, in_degrees=False)
            eyes_dist = get_eyes_dist(face.all_points)
            # print("e", pos0)
            # obj.set_rotation(Vector3(((angle[0] - pi2), -(angle[1] - pi2), 0)))
            # print(x_angle, -(x_angle - pi / 2))
            # a = [p.z for p in face.all_points]
            # print(sum(a)/len(a), min(a), max(a))
            lob = draw_face3d(scene3d, start_position, face, pos0, face_cof, objects)
            print(int(lob.z), face_cof)
            camera3d_.eye_position = Vector3(lob)
        # cube_w.position = camera3d_.get_window_pos()
        # print(camera3d_.eye_position)
        producer.show()

        if TYP == 1:
            draw_lines(camera3d, [lob], tab.points)
            processing_window(camera3d, sys3d, Vector3(lob), [tab], )

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
