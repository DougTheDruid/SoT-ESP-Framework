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

# True=Enabled & False=Disabled for each relevant config items
CONFIG = {
    "CREWS_ENABLED": True,
    "SHIPS_ENABLED": False
}

# Used to track unique crews
crew_tracker = {}

version = "1.5.0"

# Config specification for logging file
logging.basicConfig(filename='DougsESP.log', level=logging.DEBUG,
                    format='%(asctime)s %(levelname)s %(message)s', filemode="w")
logger = logging.getLogger()

# Offset values for the text labels from the circles we draw to the screen
TEXT_OFFSET_X = 13
TEXT_OFFSET_Y = -5

# Information on SoT height and width. Used here and in main.py to display
# data to the screen. May need to manually override if wonky
try:
    window = win32gui.FindWindow(None, "Sea of Thieves")
    SOT_WINDOW = win32gui.GetWindowRect(window)  # (x1, y1, x2, y2)
    SOT_WINDOW_H = SOT_WINDOW[3] - SOT_WINDOW[1]
    SOT_WINDOW_W = SOT_WINDOW[2] - SOT_WINDOW[0]
except Exception as e:
    logger.error("Unable to find SoT window; exiting.")
    exit(-1)

# Creates a pyglet "Batch" that we draw our information to. Effectively serves
# as a piece of paper, so we save render cost because its 2D
main_batch = Batch()

# Load our offset json file
with open("offsets.json") as infile:
    OFFSETS = json.load(infile)


def dot(array_1: tuple, array_2: tuple) -> float:
    """
    Python-converted version of Gummy's External SoT v2 vMatrix Dot method (No
    Longer Avail). Takes two lists and multiplies the same index across both
    lists, and adds them together. (Need Source)
    :param tuple array_1: Presumably some array about our player position
    :param tuple array_2: Presumably some array about the dest actor position
    :rtype: float
    :return: The result of a math equation between those two arrays
    """
    if array_2[0] == 0 and array_2[1] == 0 and array_2[2] == 0:
        return 0.0

    return array_1[0] * array_2[0] + array_1[1] \
           * array_2[1] + array_1[2] * array_2[2]


def object_to_screen(player: dict, actor: dict) -> tuple:
    """
    Using the player and an actors coordinates, determine where on the screen
    an object should be displayed. Assumes your screen is 2560x1440

    Python-converted version of Gummy's External SoT v2 WorldToScreen method:
    (No Longer Avail; Need Source)

    :param player: The player coordinate dictionary
    :param actor: An actor coordinate dictionary
    :rtype: tuple
    :return: tuple of x and y screen coordinates to display where the actor is
    on screen
    """
    try:
        player_camera = (player.get("cam_x"), player.get("cam_y"),
                         player.get("cam_z"))
        temp = make_v_matrix(player_camera)

        v_axis_x = (temp[0][0], temp[0][1], temp[0][2])
        v_axis_y = (temp[1][0], temp[1][1], temp[1][2])
        v_axis_z = (temp[2][0], temp[2][1], temp[2][2])

        v_delta = (actor.get("x") - player.get("x"),
                   actor.get("y") - player.get("y"),
                   actor.get("z") - player.get("z"))
        v_transformed = [dot(v_delta, v_axis_y),
                         dot(v_delta, v_axis_z),
                         dot(v_delta, v_axis_x)]

        # Credit https://github.com/AlexBurneikis
        # No valid screen coordinates if its behind us
        if v_transformed[2] < 1.0:
            return False

        fov = player.get("fov")
        screen_center_x = SOT_WINDOW_W / 2
        screen_center_y = SOT_WINDOW_H / 2

        tmp_fov = math.tan(fov * math.pi / 360)

        x = screen_center_x + v_transformed[0] * (screen_center_x / tmp_fov) \
            / v_transformed[2]
        if x > SOT_WINDOW_W or x < 0:
            return False
        y = screen_center_y - v_transformed[1] * \
            (screen_center_x / tmp_fov) \
            / v_transformed[2]
        if y > SOT_WINDOW_H or y < 0:
            return False

        return int(x), int(SOT_WINDOW_H - y)
    except Exception as w2s_error:
        logger.error(f"Couldn't generate screen coordinates for entity: {w2s_error}")


def make_v_matrix(rot: tuple) -> list:
    """
    Builds data around how the camera is currently rotated.

    Python-converted version of Gummy's External SoT v2 Matrix method:
    (No Longer Avail; Need Source)

    :param rot: The player objects camera rotation information
    :rtype: list
    :return: A list of lists containing data about the rotation of our actor
    """
    rad_pitch = (rot[0] * math.pi / 180)
    rad_yaw = (rot[1] * math.pi / 180)
    rad_roll = (rot[2] * math.pi / 180)

    sin_pitch = math.sin(rad_pitch)
    cos_pitch = math.cos(rad_pitch)
    sin_yaw = math.sin(rad_yaw)
    cos_yaw = math.cos(rad_yaw)
    sin_roll = math.sin(rad_roll)
    cos_roll = math.cos(rad_roll)

    matrix = [[0.0, 0.0, 0.0], [0.0, 0.0, 0.0], [0.0, 0.0, 0.0]]
    matrix[0][0] = cos_pitch * cos_yaw
    matrix[0][1] = cos_pitch * sin_yaw
    matrix[0][2] = sin_pitch

    matrix[1][0] = sin_roll * sin_pitch * cos_yaw - cos_roll * sin_yaw
    matrix[1][1] = sin_roll * sin_pitch * sin_yaw + cos_roll * cos_yaw
    matrix[1][2] = -sin_roll * cos_pitch

    matrix[2][0] = -(cos_roll * sin_pitch * cos_yaw + sin_roll * sin_yaw)
    matrix[2][1] = cos_yaw * sin_roll - cos_roll * sin_pitch * sin_yaw
    matrix[2][2] = cos_roll * cos_pitch
    return matrix


def calculate_distance(obj_to: dict, obj_from: dict) -> int:
    """
    Determines the distances From one object To another in meters, rounding
    to whatever degree of precision you request
    (**2 == ^2)

    Note: Can convert the int() to a round() if you want more precision

    :param obj_to: A coordinate dict for the destination object
    :param obj_from: A coordinate dict for the origin object
    :rtype: int
    :return: the distance in meters from obj_from to obj_to
    """
    return int(math.sqrt((obj_to.get("x") - obj_from.get("x")) ** 2 +
                         (obj_to.get("y") - obj_from.get("y")) ** 2 +
                         (obj_to.get("z") - obj_from.get("z")) ** 2))


def initialize_window():
    """
    Initializes our window with a given label
    """
    b_label = Label(b64decode('RG91Z1RoZURydWlkJ3MgRVNQIEZyYW1ld29yaw==').decode("utf-8"),
                    x=SOT_WINDOW_W - 537, y=10, font_size=24, bold=True,
                    color=(127, 127, 127, 65), batch=main_batch)
    return b_label
