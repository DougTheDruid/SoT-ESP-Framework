import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import struct
from helpers import OFFSETS, crew_tracker


from Modules.display_object import DisplayObject

# Debugging the imported values
print("OFFSETS:", OFFSETS)  # Debugging the value of OFFSETS
print("Crew Tracker:", crew_tracker)  # Debugging the crew tracker

class Crews(DisplayObject):
    """
    Class to generate information about the crews current on our server
    """

    def __init__(self, memory_reader, actor_id, address):
        """
        Collects all of the data about the crews currently on our server.
        :param memory_reader: The SoT MemoryHelper Object we use to read memory
        :param actor_id: The actor ID of our CrewService. Used to validate if
        there is an unexpected change
        :param address: The address in which our CrewService lives
        """
        # Initialize our super-class
        super().__init__(memory_reader)

        self.rm = memory_reader
        self.actor_id = actor_id
        self.address = address

        # Collect and store information about the crews on the server
        self.crew_info = self._get_crews_info()

        # Sum all of the crew sizes into our total_players variable
        self.total_players = sum(crew['size'] for crew in self.crew_info)

        # All of our actual display information & rendering
        self.crew_str = self._built_text_string()

        # Used to track if the display object needs to be removed
        self.to_delete = False

    def _built_text_string(self):
        """
        Generates a string used for rendering. Separate function in the event
        you need to add more data or want to change formatting
        """
        output = ""
        for x, _ in enumerate(self.crew_info):  # x = crew number, _ = crew info
            # We store all of the crews in a tracker dictionary. This allows us
            # to assign each crew a "Short"-ID based on count on the server.
            short_id = crew_tracker.get(self.crew_info[x]['guid'], None)
            output += f" Crew #{short_id} - {self.crew_info[x]['size']} Pirates\n"

        return output

    def _get_crews_info(self):
        """
        Generates information about each of the crews on the server
        """
        # Debugging: Print the CrewService address and offsets
        print(f"Reading CrewService at address: {self.address}")
        print(f"Using CrewService.Crews offset: {OFFSETS.get('CrewService.Crews')}")

        # Find the starting address for our Crews TArray
        crew_raw = self.rm.read_bytes(self.address + OFFSETS.get('CrewService.Crews'), 16)
        print(f"Crew Raw Data: {crew_raw}")  # Debugging

        # (Crews_Data<Array>, Crews length, Crews max)
        try:
            crews = struct.unpack("<Qii", crew_raw)
            print(f"Crews Data Unpacked: {crews}")  # Debugging
        except struct.error as e:
            print(f"Struct unpacking error: {e}")
            return []

        # Will contain all of our condensed Crew Data
        crews_data = []

        # For each crew on the server
        for x in range(0, crews[1]):
            # Debugging: Print which crew is being processed
            print(f"Processing crew #{x + 1}")

            # Each crew has a unique ID composed of four ints
            crew_guid_raw = self.rm.read_bytes(crews[0] + (OFFSETS.get('Crew.Size') * x), 16)
            crew_guid = struct.unpack("<iiii", crew_guid_raw)
            print(f"Crew GUID: {crew_guid}")  # Debugging

            # Read the TArray of Players on the specific Crew
            crew_raw = self.rm.read_bytes(
                crews[0] + OFFSETS.get('Crew.Players') + (OFFSETS.get('Crew.Size') * x), 16
            )
            crew = struct.unpack("<Qii", crew_raw)
            print(f"Crew Players Data: {crew}")  # Debugging

            # If our crew has more than 0 people, we care about it
            if crew[1] > 0:
                crew_data = {
                    "guid": crew_guid,
                    "size": crew[1]
                }
                crews_data.append(crew_data)

                # Add the crew GUID to the tracker if not already present
                if crew_guid not in crew_tracker:
                    crew_tracker[crew_guid] = len(crew_tracker) + 1
                print(f"Crew Tracker Updated: {crew_tracker}")  # Debugging

        return crews_data

    def update(self, my_coords):  # pylint: disable=unused-argument
        """
        A method to update all the interesting data about the crews on our server
        """
        # Debugging: Check actor ID
        current_actor_id = self._get_actor_id(self.address)
        print(f"Expected Actor ID: {self.actor_id}, Found Actor ID: {current_actor_id}")  # Debugging

        if current_actor_id != self.actor_id:
            print(f"Actor ID mismatch, setting to_delete flag.")  # Debugging
            self.to_delete = True
            return

        # Update crew information
        self.crew_info = self._get_crews_info()

        # Rebuild the string for displaying
        self.crew_str = self._built_text_string()
        print(f"Crew Display String: {self.crew_str}")  # Debugging
 