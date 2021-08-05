"""
@Author https://github.com/DougTheDruid
@Source https://github.com/DougTheDruid/SoT-ESP-Framework
"""


import struct
from helpers import OFFSETS
from memory_helper import ReadMemory


class DisplayObject:
    """
    Class responsible for the base functionality of pulling data from
    our memory objects. These are typically identical regardless of the actor
    type we are looking at
    """

    def __init__(self, memory_reader: ReadMemory):
        """
        Parent class to objects like Ship's. Helpful as the methods found here
        would be considered "common" and reduces redundant code.
        :param memory_reader: The SoT MemoryHelper object we are utilizing to
        read memory data from the game
        """
        self.m_r = memory_reader

    def _get_root_comp_address(self, address: int) -> int:
        """
        Function to get an AActor's root component memory address
        :param address: the base address for a given AActor
        :rtype: int
        :return: the address of an AActors root component
        """
        return self.m_r.read_ptr(
            address + OFFSETS.get("AActor.rootComponent")
        )

    def _coord_builder(self, root_comp_ptr: int, offset: int) -> dict:
        """
        Given an actor, loads the coordinates for that actor
        :param int root_comp_ptr: Actors root component memory address
        :param int offset: Offset from root component to beginning of coords,
        Often determined manually with Cheat Engine
        :rtype: dict
        :return: A dictionary containing the coordinate information
        for a specific actor
        """
        actor_bytes = self.m_r.read_bytes(root_comp_ptr + offset, 24)
        unpacked = struct.unpack("<ffffff", actor_bytes)

        coordinate_dict = {"x": unpacked[0] / 100, "y": unpacked[1] / 100,
                           "z": unpacked[2] / 100}
        return coordinate_dict
