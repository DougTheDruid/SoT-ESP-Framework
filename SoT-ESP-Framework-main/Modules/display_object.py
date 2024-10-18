"""
@Author https://github.com/DougTheDruid
@Source https://github.com/DougTheDruid/SoT-ESP-Framework
"""

import struct
import abc
from helpers import OFFSETS
from memory_helper import ReadMemory


class DisplayObject(metaclass=abc.ABCMeta):
    """
    Parent class to objects like Ship's. Responsible for the base functionality
    of pulling data from our memory objects. These are typically identical
    regardless of the actor type we are looking at; as such would be
    considered "common" and reduces redundant code.
    """

    def __init__(self, memory_reader: ReadMemory):
        """
        Some of our DisplayObject calls need to make memory reads, so we will
        ser out memory reader as a class variable.
        :param memory_reader: The SoT MemoryHelper object we are utilizing to
        read memory data from the game
        """
        self.rm = memory_reader
        self.coord_offset = OFFSETS.get('SceneComponent.ActorCoordinates')

    def _get_actor_id(self, address: int) -> int:
        """
        Function to get the AActor's ID, used to validate the ID hasn't changed
        while running a "quick" scan
        :param int address: the base address for a given AActor
        :rtype: int
        :return: The AActors ID
        """
        return self.rm.read_int(
            address + OFFSETS.get('Actor.actorId')
        )

    def _get_root_comp_address(self, address: int) -> int:
        """
        Function to get an AActor's root component memory address
        :param int address: the base address for a given AActor
        :rtype: int
        :return: the address of an AActors root component
        """
        return self.rm.read_ptr(
            address + OFFSETS.get("Actor.rootComponent")
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
        actor_bytes = self.rm.read_bytes(root_comp_ptr + offset, 24)
        unpacked = struct.unpack("<ffffff", actor_bytes)

        coordinate_dict = {"x": unpacked[0] / 100, "y": unpacked[1] / 100,
                           "z": unpacked[2] / 100}
        return coordinate_dict

    @abc.abstractmethod
    def update(self, my_coords):
        """
        Required implementation method that we can call to update
        the objects data in a quick fashion vs scanning every actor.
        """
