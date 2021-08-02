"""
@Author https://github.com/DougTheDruid
@Source https://github.com/DougTheDruid/SoT-ESP-Framework
"""


from helpers import calculate_distance, object_to_screen, main_batch, \
    TEXT_OFFSET_X, TEXT_OFFSET_Y
from mapping import ships
from display_object import DisplayObject
from pyglet.text import Label
from pyglet.shapes import Circle

SHIP_COLOR = (100, 0, 0)  # The color we want the indicator circle to be
COORD_OFFSET = 0x100


class Ship(DisplayObject):
    """
    Class to generate information for a ship object in memory
    """

    def __init__(self, memory_reader, actor_id, address, my_coords, raw_name):
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
        self.actor_id = actor_id
        self.address = address
        self.actor_root_comp_ptr = self._get_root_comp_address(address)
        self.my_coords = my_coords
        self.raw_name = raw_name
        self.name = ships.get(self.raw_name).get("Name")
        self.coords = self._coord_builder(self.actor_root_comp_ptr,
                                          COORD_OFFSET)
        self.distance = calculate_distance(self.coords, self.my_coords)

        if "Near" not in self.name and self.distance < 1720:
            return

        self.screen_coords = object_to_screen(self.my_coords, self.coords)
        self.color = SHIP_COLOR

        self.text_str = self._built_text_string()
        self.text_render = self._build_text_render()
        self.icon = self._build_circle_render()

        self.to_delete = False

    def _build_circle_render(self):
        """
        Creates our render
        """
        if self.screen_coords:
            return Circle(self.screen_coords[0], self.screen_coords[1], 10,
                          color=self.color, batch=main_batch)
        else:
            return Circle(0, 0, 10, color=self.color, batch=main_batch)

    def _built_text_string(self) -> str:
        return f"{self.name} - {self.distance}m"

    def _build_text_render(self) -> Label:
        """
        Function to build our display text string. Seperated out in the event
        you add more information about a ship that you need to customize
        the display for (% sunk, holes, etc)
        :type: Label
        :return: What text we want displayed next to the ship
        """
        if self.screen_coords:
            return Label(self.text_str, x=self.screen_coords[0] + TEXT_OFFSET_X,
                         y=self.screen_coords[1] + TEXT_OFFSET_Y, batch=main_batch)

        else:
            return Label(self.text_str, x=0,
                         y=0, batch=main_batch)

    def update(self, my_coords):
        """
        A generic method to update all the interesting data about a ship
        object, to be called when seeking to perform an update on the
        Actor without doing a full-scan of all actors in the game.

        1. Determinine if the actor is what we expect it to be
        2. See if any data has changed
        3. Update the data if something has changed

        In theory the step 2/3 will help us cut down on label-rendering time
        in the future (if it does indeed consume resources)
        :rtype: dict
        :return: A dictionary of information about a Ship object
        """
        if self._get_actor_id(self.address) != self.actor_id:
            self.to_delete = True
            return

        self.my_coords = my_coords
        self.coords = self._coord_builder(self.actor_root_comp_ptr,
                                          COORD_OFFSET)
        new_distance = calculate_distance(self.coords, self.my_coords)

        self.screen_coords = object_to_screen(self.my_coords, self.coords)

        if self.screen_coords:
            if self.text_render.font_size == 0:
                self.text_render.font_size = 12
            if not self.icon.visible:
                self.icon.visible = True

            self.icon.x = self.screen_coords[0]
            self.icon.y = self.screen_coords[1]
            self.text_render.x = self.screen_coords[0] + TEXT_OFFSET_X
            self.text_render.y = self.screen_coords[1] + TEXT_OFFSET_Y

            self.distance = new_distance
            self.text_str = self._built_text_string()
            self.text_render.text = self.text_str
        else:
            self.icon.visible = False
            self.text_render.font_size = 0
