import pygame
from pygame._sdl2 import Window
import win32api
import win32con
import win32gui
import face_mesh
from smooth import np_smooth

fuchsia = (255, 0, 128)  # Transparency color
fuchsia = (10, 10, 10)
cam = face_mesh.init_cam()
cam_size = face_mesh.get_cam_size(cam)
H = 800
SIZE = cam_size[0] * H / cam_size[1], H

pygame.init()
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
    for p1, p2 in points:
        p1, p2 = (p1.x, p1.y), (p2.x, p2.y)
        keys.add(p1)
        d[p1] = p2
    r = list()
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
    rx = [p[0] for p in r]
    ry = [p[1] for p in r]
    rxs = np_smooth(rx, 20)
    rys = np_smooth(ry, 20)
    r = list(zip(rxs, rys))
    return [(r[i - 1], r[i]) for i in range(1, len(r))]


def draw_face():
    width, height = SIZE
    figures = face_mesh.get_face_mesh_from_cam(cam)
    colors = "white", "white", "red", "red", "green", "yellow", "blue", "purple", "lightblue", "lightblue"
    # colors = (10, 10, 10), (10, 10, 10), (10, 10, 10), (10, 10, 10), (10, 10, 10), (10, 10, 10), \
    #     (10, 10, 10), (200, 200, 200), (200, 200, 200)
    a = 2
    for color, points in zip(colors, figures):
        # print(color, len(points))
        color2 = color
        points = smooth_line(points)
        # print(color, len(points))
        for pt1, pt2 in points:
            x = width - int(pt1[0] * width)
            y = int(pt1[1] * height)
            x2 = width - int(pt2[0] * width)
            y2 = int(pt2[1] * height)
            pygame.draw.line(screen, color2, (x + a, y), (x2 + a, y2), 1)
            pygame.draw.line(screen, color2, (x, y - a), (x2, y2 - a), 1)
            pygame.draw.line(screen, color2, (x - a, y), (x2 - a, y2), 1)
            pygame.draw.line(screen, color2, (x, y + a), (x2, y2 + a), 1)
            pygame.draw.line(screen, color, (x, y), (x2, y2), 3)
            # pygame.draw.aaline(screen, color, (x+a, y+a), (x2+a, y2+a), 20)


done = False
last_surface = pygame.Surface(SIZE)
last_surface.set_colorkey(fuchsia)
while not done:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            done = True
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_h:
                wx, wy = window.position
                set_flag(pygame.NOFRAME)
                win32gui.SetLayeredWindowAttributes(hwnd, win32api.RGB(*fuchsia), 0, win32con.LWA_COLORKEY)
                win32gui.SetWindowPos(hwnd, win32con.HWND_TOPMOST, wx, wy, 0, 0, win32con.SWP_NOSIZE)
            if event.key == pygame.K_s:
                set_flag(0)
    screen.fill(fuchsia)  # Transparent background
    last_surface.set_alpha(50)
    # screen.blit(last_surface, (0, 0))

    draw_face()
    last_surface.blit(screen, (0, 0))
    pygame.display.update()
