"""
@Author https://github.com/DougTheDruid
@Source https://github.com/DougTheDruid/SoT-ESP-Framework
"""


from helpers import DEFAULT_FONT, calculate_distance, object_to_screen
from mapping import ships
from display_object import DisplayObject

ships_color = (100, 0, 0)  # The color we want the indicator circle to be


class Ship(DisplayObject):
    """
    Class to generate information for a ship object in memory
    """

    def __init__(self, memory_reader, address, my_coords, raw_name):
        """
        Upon initialization of this class, we immediately initialize the
        DisplayObject parent class as well (to utilize common methods)
        We then set our class variables and perform some basic init functions
        like finding the actors base address and converting the "raw" name
        to a more readable name per our Mappings
        :param memory_reader: The SoT MemoryHelper Object we use to read memory
        :param address: The address in which the AActor begins
        :param my_coords: a dictionary of the local players coordinates
        :param raw_name: The raw actor name used to translate w/ mapping.py
        """
        super().__init__(memory_reader)
        self.rm = memory_reader
        self.address = address
        self.actor_root_comp_ptr = self._get_root_comp_address(address)
        self.my_coords = my_coords
        self.raw_name = raw_name
        self.name = ships.get(self.raw_name).get("Name")

    @staticmethod
    def _build_text_render(ship_info) -> tuple:
        """
        Function to render text to be used in PyGame for display.
        :param ship_info: A dictionary of ship information, used to render text
        with relevant information
        :type: tuple
        :return: a tuple of rendered font for pygame, and the color to make
        the circle that appears on screen
        """
        to_display = f"{ship_info.get('Common_Name')} - " \
                     f"{ship_info.get('Distance')}m"
        return DEFAULT_FONT.render(to_display, False,
                                   (255, 255, 255)), ships_color

    def get_ship_info(self) -> dict:
        """
        A generic method to generate all the interesting data about a ship
        object, to be called after initialization.

        Get the objects coordinates, and distance to your coordinates, then
        determines if the object should be on screen or not (no sense rendering
        if its off screen), builds the on screen info if necessary, and
        returns that data
        :rtype: dict
        :return: A dictionary of information about a Ship object
        """
        coords = self._coord_builder(self.actor_root_comp_ptr, 0x100)
        distance = calculate_distance(coords, self.my_coords, 1)

        screen_coords = object_to_screen(self.my_coords, coords)
        if screen_coords:
            if "Near" not in self.name and distance < 1720:
                return

            ship_info = {
                "Type": "Ship",
                "Common_Name": self.name,
                "Coordinates": coords,
                "Screen_Coordinates": screen_coords,
                "Distance": distance,
            }
            text, color = self._build_text_render(ship_info)
            ship_info["Text"] = text
            ship_info["Color"] = color
            return ship_info
