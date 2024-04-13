import pygame
from pygame._sdl2 import Window
import win32api
import win32con
import win32gui
import face_mesh

fuchsia = (255, 0, 128)  # Transparency color
fuchsia = (0, 0, 0)
cam = face_mesh.init_cam()
cam_size = face_mesh.get_cam_size(cam)
H = 400
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


def draw_face():
    width, height = SIZE
    figures = face_mesh.get_face_mesh_from_cam(cam)
    colors = "white", "red", "green", "blue", "white", "yellow", "purple"
    for color, points in zip(colors, figures):
        for pt1, pt2 in points:
            x = width - int(pt1.x * width)
            y = int(pt1.y * height)
            x2 = width - int(pt2.x * width)
            y2 = int(pt2.y * height)

            # pygame.draw.circle(screen, "red", (x, y), 5)
            # pygame.draw.circle(screen, "red", (x2, y2), 5)
            pygame.draw.line(screen, color, (x, y), (x2, y2), 5)


done = False
last_surface = pygame.Surface(SIZE)
# last_surface.set_colorkey(fuchsia)
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
    last_surface.set_alpha(220)
    screen.blit(last_surface, (0, 0))

    draw_face()
    last_surface.blit(screen, (0, 0))
    pygame.display.update()
