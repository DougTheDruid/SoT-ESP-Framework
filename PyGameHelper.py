"""
@Author https://github.com/DougTheDruid
@Source https://github.com/DougTheDruid/SoT-ESP-Framework
"""


import pygame
from ctypes import windll
import win32api
import win32con
import win32gui
import os

SetWindowPos = windll.user32.SetWindowPos
NOSIZE = 1
NOMOVE = 2
TOPMOST = -1
NOT_TOPMOST = -2
fuchsia = (255, 0, 128)


class PyGameHelper:
    """
    Object to wrap some of the initialization functions of PyGame
    """
    def __init__(self):
        # Initialize Pygame,find the Sea of Thieves window area, and move the
        # Pygame window to overlay Sea of Thieves

        pygame.init()

        window = win32gui.FindWindow(None, "Sea of Thieves")
        self.windows_area = win32gui.GetWindowRect(window)

        os.environ['SDL_VIDEO_WINDOW_POS'] = "%d,%d" % (self.windows_area[0], self.windows_area[1])

        # Creates a pygame screen that is borderless at our known window area
        self.screen = pygame.display.set_mode((self.windows_area[2] - self.windows_area[0],
                                               self.windows_area[3] - self.windows_area[1]),
                                              pygame.NOFRAME)

        # Forces the window to be "on top", sets the layer to be transparent
        # using the fucsia color, and makes it so it cannot move.
        hwnd = pygame.display.get_wm_info()["window"]
        win32gui.SetWindowLong(hwnd, win32con.GWL_EXSTYLE,
                               win32gui.GetWindowLong(hwnd, win32con.GWL_EXSTYLE) | win32con.WS_EX_LAYERED)
        win32gui.SetLayeredWindowAttributes(hwnd, win32api.RGB(*fuchsia), 0, win32con.LWA_COLORKEY)

        z_order = (NOT_TOPMOST, TOPMOST)[True]  # choose a flag according to bool
        SetWindowPos(hwnd, z_order, 0, 0, 0, 0, NOMOVE | NOSIZE)

        # One single pygame font to be used for any rendering done outside of
        # specific object classes (IE: Ships, which would be handled using the
        # Helpers.py font renderer)
        pygame.font.init()
        self.my_font = pygame.font.SysFont('Microsoft Sans Serif', 15)
