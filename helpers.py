"""
@Author https://github.com/DougTheDruid
@Source https://github.com/DougTheDruid/SoT-ESP-Framework
"""

import math
import json
import logging
from base64 import b64decode
import win32gui
from pyglet.graphics import Batch
from pyglet.text import Label

# Configuration for enabling/disabling features
CONFIG = {
    "CREWS_ENABLED": True,
    "SHIPS_ENABLED": False
}

# Tracker for unique crews
crew_tracker = {}

version = "1.6.0"

# Set up logging to a file
logging.basicConfig(filename='DougsESP.log', level=logging.DEBUG,
                    format='%(asctime)s %(levelname)s %(message)s', filemode="w")
logger = logging.getLogger()

# Offset values for text labels from the circles drawn on the screen
TEXT_OFFSET_X = 13
TEXT_OFFSET_Y = -5

# Information on Sea of Thieves window dimensions
try:
    window = win32gui.FindWindow(None, "Sea of Thieves")
    SOT_WINDOW = win32gui.GetWindowRect(window)  # (x1, y1, x2, y2)
    SOT_WINDOW_H = SOT_WINDOW[3] - SOT_WINDOW[1]
    SOT_WINDOW_W = SOT_WINDOW[2] - SOT_WINDOW[0]
except Exception as e:
    logger.error("Unable to find SoT window; exiting. Error: %s", e)
    exit(-1)

# Create a Pyglet batch for rendering
main_batch = Batch()

# Load offset data from a JSON file
try:
    with open("offsets.json") as infile:
        OFFSETS = json.load(infile)
except FileNotFoundError:
    logger.error("Offsets file not found; please ensure offsets.json exists.")
    exit(-1)
except json.JSONDecodeError:
    logger.error("Error decoding JSON from offsets.json; exiting.")
    exit(-1)


def dot(array_1: tuple, array_2: tuple) -> float:
    """
    Calculates the dot product of two 3D vectors.
    :param tuple array_1: First vector
    :param tuple array_2: Second vector
    :rtype: float
    :return: The dot product
    """
    return sum(a * b for a, b in zip(array_1, array_2))


def object_to_screen(player: dict, actor: dict) -> tuple:
    """
    Converts world coordinates to screen coordinates.
    :param player: Player's coordinate dictionary
    :param actor: Actor's coordinate dictionary
    :rtype: tuple
    :return: Screen coordinates (x, y) or False if behind the player
    """
    try:
        player_camera = (player.get("cam_x"), player.get("cam_y"), player.get("cam_z"))
        temp = make_v_matrix(player_camera)

        v_delta = (actor.get("x") - player.get("x"),
                   actor.get("y") - player.get("y"),
                   actor.get("z") - player.get("z"))
        v_transformed = [dot(v_delta, axis) for axis in temp]

        if v_transformed[2] < 1.0:  # Behind the player
            return False

        fov = player.get("fov")
        screen_center_x = SOT_WINDOW_W / 2
        screen_center_y = SOT_WINDOW_H / 2
        tmp_fov = math.tan(fov * math.pi / 360)

        x = screen_center_x + v_transformed[0] * (screen_center_x / tmp_fov) / v_transformed[2]
        y = screen_center_y - v_transformed[1] * (screen_center_x / tmp_fov) / v_transformed[2]

        if 0 <= x <= SOT_WINDOW_W and 0 <= y <= SOT_WINDOW_H:
            return int(x), int(SOT_WINDOW_H - y)
        return False
    except Exception as w2s_error:
        logger.error("Couldn't generate screen coordinates for entity: %s", w2s_error)
        return False


def make_v_matrix(rot: tuple) -> list:
    """
    Creates a rotation matrix based on camera rotation.
    :param rot: Camera rotation (pitch, yaw, roll)
    :rtype: list
    :return: 3x3 rotation matrix
    """
    rad_pitch, rad_yaw, rad_roll = [math.radians(angle) for angle in rot]

    sin_pitch, cos_pitch = math.sin(rad_pitch), math.cos
