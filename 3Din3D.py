from cmath import pi

import numpy as np
import pygame3d
import pygame as pg

from face_mesh import get_face_points, get_frame, init_cam
from face_position import get_base_point, face2angle

screen = pg.display.set_mode((780, 420))
pi2 = pi / 2


def main():
    cube = np.array([(0, 0, 0), (1, 0, 0), (1, 1, 0), (0, 1, 0), (0, 0, 1), (1, 0, 1), (1, 1, 1), (0, 1, 1)])
    cube = pygame3d.move(cube, np.array((-0.5, -0.5, -0.5)))
    cam3d = pygame3d.Camera()

    cam = init_cam(0)
    base_point = get_base_point(get_face_points(get_frame(cam)))

    running = True
    while running:
        [exit() for event in pg.event.get(pg.QUIT)]
        screen.fill("black")

        all_points = get_face_points(get_frame(cam))
        if all_points:
            x_angle, y_angle = face2angle(all_points, base_point, in_degrees=False)
            print(x_angle, -(x_angle - pi / 2))
        ncube = pygame3d.rotate(cube, ((x_angle - pi2) / 2, (y_angle - pi2) / 2, 0))
        cam3d.draw_objects(screen, [ncube])

        pg.display.flip()


if __name__ == '__main__':
    main()
