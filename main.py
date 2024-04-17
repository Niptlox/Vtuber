from typing import NamedTuple

import pygame, time
from pygame._sdl2 import Window
import win32api
import win32con
import win32gui
import face_mesh

from smooth import np_smooth

colorkey = (255, 0, 255)  # Transparency color
# colorkey = (10, 10, 10)
# colorkey = (0, 0, 0, 0)

SORTED = False
ABRAKADABRA = False
SHUFFLE = False
SPLINE_COF = 10

if SHUFFLE:
    face_mesh.shuffle_contours()

cam = face_mesh.init_cam(1)
cam_size = face_mesh.get_cam_size(cam)
H = 1000
SIZE = cam_size[0] * H / cam_size[1], H

pygame.init()
pygame.font.init()
font = pygame.font.SysFont("", 9)
screen = pygame.display.set_mode(SIZE)  # For borderless, use pygame.NOFRAME
window = Window.from_display_module()

# -------
hwnd = pygame.display.get_wm_info()["window"]
win32gui.SetWindowLong(hwnd, win32con.GWL_EXSTYLE,
                       win32gui.GetWindowLong(hwnd, win32con.GWL_EXSTYLE) | win32con.WS_EX_LAYERED)


# --------

def set_flag(flag):
    global screen
    screen = pygame.display.set_mode(SIZE, flag)


def smooth_line(points):
    if not points:
        return []
    d = {}
    keys = set()
    r = list()
    for p1, p2 in points:
        # print(p1.z)
        p1, p2 = (p1.x, p1.y), (p2.x, p2.y)
        r.append(p1)
        keys.add(p1)
        d[p1] = p2
    if SORTED:
        r.sort()
    if ABRAKADABRA:
        #     ===========
        r = list()
        keys = set(sorted(keys))
        while keys:
            p1 = keys.pop()
            r.append(p1)
            # keys.remove(p1)
            while p1 in d and keys:
                p1 = d[p1]
                r.append(p1)
                if p1 in keys:
                    keys.remove(p1)
                elif p1 in d and d[p1] not in keys:
                    # keys.remove(p1)
                    # keys.remove(d[p1])
                    break
        #             ================
    rx = [p[0] for p in r]
    ry = [p[1] for p in r]
    rxs = np_smooth(rx, SPLINE_COF, -0.2, abra=True)
    rys = np_smooth(ry, SPLINE_COF, -0.2, abra=True)
    r = list(zip(rxs, rys))
    return [(r[i - 1], r[i]) for i in range(1, len(r))]


def draw_face(surface):
    # surface.fill(colorkey)  # Transparent background
    width, height = SIZE
    face = face_mesh.get_face(cam)

    gray = (230, 240, 240)
    colors = "blue", gray, gray, "red", "red", "green", "yellow", "purple", "lightblue", "lightblue"
    # colors = (10, 10, 10), (10, 10, 10), (10, 10, 10), (10, 10, 10), (10, 10, 10), (10, 10, 10), \
    #     (10, 10, 10), (200, 200, 200), (200, 200, 200)
    a = 2
    i = 0
    for color, points in zip(colors, face.contours):
        # print(color, len(points))
        color = pygame.color.Color(color)
        if i == 8 and face.state.left_eye_closed:
            color.a = 250 * face.state.left_eye_cof
        if i == 9 and face.state.right_eye_closed:
            color.a = 250 * face.state.right_eye_cof
        color2 = color
        points = smooth_line(points)
        # print(color, len(points))
        for pt1, pt2 in points:
            x = width - int(pt1[0] * width)
            y = int(pt1[1] * height)
            x2 = width - int(pt2[0] * width)
            y2 = int(pt2[1] * height)
            pygame.draw.line(surface, color2, (x + a, y), (x2 + a, y2), 2)
            pygame.draw.line(surface, color2, (x, y - a), (x2, y2 - a), 1)
            pygame.draw.line(surface, color2, (x - a, y), (x2 - a, y2), 2)
            pygame.draw.line(surface, color2, (x, y + a), (x2, y2 + a), 1)
            pygame.draw.line(surface, color, (x, y), (x2, y2), 3)

            # pygame.display.update()
            # pygame.event.get()
            # time.sleep(0.01)
        i += 1


screen.set_colorkey(colorkey)
done = False
last_surface = pygame.Surface(SIZE)
last_surface.set_colorkey(colorkey)
history_len = 1
history_screen = [None] * history_len
while not done:
    screen.fill(colorkey)
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            done = True
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_h:
                wx, wy = window.position
                set_flag(pygame.NOFRAME)
                win32gui.SetLayeredWindowAttributes(hwnd, win32api.RGB(*colorkey), 0, win32con.LWA_COLORKEY)
                win32gui.SetWindowPos(hwnd, win32con.HWND_TOPMOST, wx, wy, 0, 0, win32con.SWP_NOSIZE)
            if event.key == pygame.K_s:
                set_flag(0)
    # last_surface.set_alpha(50)
    # screen.blit(last_surface, (0, 0))
    surface = pygame.Surface(SIZE)
    surface.fill(colorkey)
    surface.set_colorkey(colorkey)

    draw_face(screen)

    history_screen.pop(0)
    history_screen.append(surface)
    for shot in history_screen:
        if shot:
            screen.blit(shot, (0, 0))

    pygame.display.update()
    # time.sleep(0.01)
