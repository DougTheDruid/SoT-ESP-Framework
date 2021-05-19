"""
@Author https://github.com/DougTheDruid
@Source https://github.com/DougTheDruid/SoT-ESP-Framework
"""


from Helpers import *
import struct


class DisplayObject:
    def __init__(self, memory_reader):
        """
        Parent class to objects like Ship's. Helpful as the methods found here
        would be considered "common" and reduces redundent code.
        :param memory_reader: The SoT MemoryHelper object we are utilizing to
        read memory data from the game
        """
        self.rm = memory_reader

    def _get_root_comp_address(self, address: int) -> int:
        """
        Function to get an AActor's root component memory address
        :param address: the base address for a given AActor
        :rtype: int
        :return: the address of an AActors root component
        """
        return self.rm.read_ptr(
            address + OFFSETS.get('AActor.rootComponent')
        )

    def _coord_builder(self, root_comp_ptr, offset) -> dict:
        """
        Given an actor, loads the coordinates for that actor
        :param int root_comp_ptr: Actors root component memory address
        :param int offset: Offset from root component to beginning of coords,
        Often determined manually with Cheat Engine
        :rtype: dict
        :return: A dictionary contianing the coordinate information
        for a specific actor
        """
        actor_bytes = self.rm.read_bytes(root_comp_ptr + offset, 24)
        unpacked = struct.unpack("<ffffff", actor_bytes)

        coordinate_dict = {"x": unpacked[0] / 100, "y": unpacked[1] / 100,
                           "z": unpacked[2] / 100}
        return coordinate_dict
