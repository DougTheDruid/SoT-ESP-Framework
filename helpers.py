"""
@Author https://github.com/DougTheDruid
@Source https://github.com/DougTheDruid/SoT-ESP-Framework
"""


import math
import json
import pygame
from win32api import GetSystemMetrics

# True=Enabled & False=Disabled for each of the config items
CONFIG = {
    "WORLD_PLAYERS_ENABLED": True,
    "SHIPS_ENABLED": False,
}

# Information on your monitor height and width. Used here and
# in main.py to display data to the screen. May need to manually override if
# wonky
SCREEN = {
    "x": GetSystemMetrics(0),
    "y": GetSystemMetrics(1)
}


# Font renderer used for objects such as Ships
pygame.font.init()
DEFAULT_FONT = pygame.font.SysFont("Microsoft Sans Serif", 15)


with open("offsets.json") as infile:
    OFFSETS = json.load(infile)


def dot(array_1: list, array_2: list) -> float:
    """
    Python-converted version of Gummy's External SoT v2 vMatrix Dot method:
    https://tinyurl.com/hcpafjs

    :rtype: float
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
    https://tinyurl.com/3bef29jd

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

        if v_transformed[2] < 1.0:
            v_transformed[2] = 1.0

        fov = player.get("fov")
        screen_center_x = SCREEN.get("x") / 2
        screen_center_y = SCREEN.get("y") / 2

        tmp_fov = math.tan(fov * math.pi / 360)

        x = screen_center_x + v_transformed[0] * (screen_center_x / tmp_fov) \
            / v_transformed[2]
        if x > SCREEN.get("x") or x < 0:
            return False
        y = screen_center_y - v_transformed[1] * \
            (screen_center_x / math.tan(fov * math.pi / 360)) \
            / v_transformed[2]
        if y > SCREEN.get("y") or y < 0:
            return False

        return x, y
    except Exception as e:
        print(f"Couldnt gen screen coordinates for {actor}: {e}")


def make_v_matrix(rot: dict) -> list:
    """
    Builds data around how the camera is currently rotated.

    Python-converted version of Gummy's External SoT v2 Matrix method:
    https://tinyurl.com/3bt9brm3

    :param rot: The player objects camera rotation information
    :rtype: list
    :return:
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


def calculate_distance(obj_to: dict, obj_from: dict,
                       round_to: int = 0) -> float:
    """
    Determines the distances From one object To another in meters, rounding
    to whatever degree of precision you request

    :param obj_to: A coordinate dict for the destination object
    :param obj_from: A coordinate dict for the origin object
    :param round_to: How precise to be in the return
    :return: the distance in meters from obj_from to obj_to
    """
    return round(math.sqrt(math.pow((obj_to.get("x") - obj_from.get("x")), 2) +
                           math.pow((obj_to.get("y") - obj_from.get("y")), 2) +
                           math.pow((obj_to.get("z") - obj_from.get("z")), 2)),
                 round_to)
