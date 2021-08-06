"""
@Author https://github.com/DougTheDruid
@Source https://github.com/DougTheDruid/SoT-ESP-Framework
For community support, please contact me on Discord: DougTheDruid#2784
"""


import struct
from memory_helper import ReadMemory
from mapping import ship_keys
from helpers import OFFSETS, CONFIG
from ship import Ship


STEAM_VERSION = False

UWORLD_PATTERN = "48 8B 05 ? ? ? ? 48 8B 88 ? ? ? ? 48 85 C9 74 06 48 8B 49 70"
GOBJECT_PATTERN = "89 0D ? ? ? ? 48 8B DF 48 89 5C 24"
GNAME_PATTERN = "48 8B 1D ? ? ? ? 48 85 DB 75 ? B9 08 04 00 00"

if STEAM_VERSION:
    UWORLDBASE = 0x6E685B
    GOBJECTBASE = 0x15D11DB
    GNAMEBASE = 0x153DF2A

else:
    UWORLDBASE = 0x6E5F5B
    GOBJECTBASE = 0x15E9D14
    GNAMEBASE = 0x14FFCF8


class SoTMemoryReader:
    """
    Wrapper class to handle reading data from the game, parsing what is
    important, and returning it to be shown by pygame
    """

    def __init__(self):
        """
        Upon initialization of this object, we want to find the base address
        for the SoTGame.exe, then begin to load in the static addresses for the
        uWorld, gName, gObject, and uLevel objects.

        We also poll the local_player object to get a first round of coords.
        When running read_actors, we update the local players coordinates
        using the camera-manager object

        Also initialize a number of class variables which help us cache some
        basic information
        """
        self.rm = ReadMemory("SoTGame.exe")
        base_address = self.rm.base_address

        u_world_offset = self.rm.read_ulong(base_address + UWORLDBASE + 3)
        u_world = base_address + UWORLDBASE + u_world_offset + 7
        self.world_address = self.rm.read_ptr(u_world)

        g_name_offset = self.rm.read_ulong(base_address + GNAMEBASE + 3)
        self.g_name = self.rm.read_ptr(base_address + GNAMEBASE
                                       + g_name_offset + 7)

        g_objects_offset = self.rm.read_ulong(base_address + GOBJECTBASE + 2)
        g_objects = base_address + GOBJECTBASE + g_objects_offset + 22
        self.g_objects = self.rm.read_ptr(g_objects)

        self.u_level = self.rm.read_ptr(self.world_address +
                                        OFFSETS.get('UWorld.PersistentLevel'))

        u_local_player = self._load_local_player()

        # self.player_controller = self.rm.read_ptr(
        #     u_local_player + OFFSETS.get('ULocalPlayer.PlayerController')
        # )

        self.my_coords = self._coord_builder(u_local_player)
        self.my_coords['fov'] = 90

        self.actor_name_map = {}
        self.server_players = []
        self.run_info = []

    def _load_local_player(self) -> int:
        """
        Returns the local player object out of uWorld.UGameInstance.
        Used to get the players coordinates before reading any actors
        :rtype: int
        :return: Memory address of the local player object
        """
        game_instance = self.rm.read_ptr(
            self.world_address + OFFSETS.get('UWorld.OwningGameInstance')
        )
        local_player = self.rm.read_ptr(
            game_instance + OFFSETS.get('UGameInstance.LocalPlayers')
        )
        return self.rm.read_ptr(local_player)

    def _coord_builder(self, actor_address: int, offset=0x78, camera=True,
                       fov=False) -> dict:
        """
        Given a specific actor, loads the coordinates for that actor given
        a number of parameters to define the output
        :param int actor_address: Actors base memory address
        :param int offset: Offset from actor address to beginning of coords
        :param bool camera: If you want the camera info as well
        :param bool fov: If you want the FoV info as well
        :rtype: dict
        :return: A dictionary containing the coordinate information
        for a specific actor
        """
        if fov:
            actor_bytes = self.rm.read_bytes(actor_address + offset, 44)
            unpacked = struct.unpack("<ffffff16pf", actor_bytes)
        else:
            actor_bytes = self.rm.read_bytes(actor_address + offset, 24)
            unpacked = struct.unpack("<ffffff", actor_bytes)

        coordinate_dict = {"x": unpacked[0]/100, "y": unpacked[1]/100,
                           "z": unpacked[2]/100}
        if camera:
            coordinate_dict["cam_x"] = unpacked[3]
            coordinate_dict["cam_y"] = unpacked[4]
            coordinate_dict["cam_z"] = unpacked[5]
        if fov:
            coordinate_dict['fov'] = unpacked[7]

        return coordinate_dict

    def _read_name(self, actor_id: int) -> str:
        """
        Looks up an actors name in the g_name DB based on the actor ID provided
        :param int actor_id: The ID for the actor we want to find the name of
        :rtype: str
        :return: The name for the actor
        """
        name_ptr = self.rm.read_ptr(self.g_name + int(actor_id / 0x4000) * 0x8)
        name = self.rm.read_ptr(name_ptr + 0x8 * int(actor_id % 0x4000))
        return self.rm.read_string(name + 0x10, 64)

    def read_actors(self):
        """
        Main game loop. Is responsible for determining how many actors to scan
        and calling assisting functions to interpret data about said actors.
        Stores all relevant information in class variables
        """
        self.run_info = []

        actor_raw = self.rm.read_bytes(self.u_level + 0xa0, 0xC)
        actor_data = struct.unpack("<Qi", actor_raw)

        self.server_players = []
        for x in range(0, actor_data[1]):
            # We start by getting the ActorID for a given actor, and comparing
            # that ID to a list of "known" id's we cache in self.actor_name_map
            raw_name = ""
            actor_address = self.rm.read_ptr(actor_data[0] + (x * 0x8))
            actor_id = self.rm.read_int(
                actor_address + OFFSETS.get('AActor.actorId')
            )
            if actor_id not in self.actor_name_map and actor_id != 0:
                try:
                    raw_name = self._read_name(actor_id)
                    self.actor_name_map[actor_id] = raw_name
                except Exception as e:
                    print(str(e))
            elif actor_id in self.actor_name_map:
                raw_name = self.actor_name_map.get(actor_id)

            # Ignore anything we cannot find a name for
            if not raw_name:
                continue

            # AthenaPlayerCameraManager contains information on the local
            # players camera object, namely coordinates and camera information.
            # Use that data and set self.my_coordinates to the camera's coords
            if raw_name == "BP_AthenaPlayerCameraManager_C":
                self.my_coords = self._coord_builder(actor_address + 0x450,
                                                     0x0, fov=True)
                continue

            # If we have Ship ESP enabled in helpers.py, and the name of the
            # actor is in our mapping.py ship_keys object, interpret the actor
            # as a ship
            if CONFIG.get('SHIPS_ENABLED') and raw_name in ship_keys:
                self.read_ships(actor_address, raw_name)

            # If we have the world players enabled in helpers.py, and the name
            # of the actor is AthenaPlayerState, we interpret the actor as a
            # player on the server.
            # NOTE: This will NOT give us information on nearby players for the
            # sake of ESP
            elif CONFIG.get('WORLD_PLAYERS_ENABLED') and "AthenaPlayerState" in raw_name:
                self.read_world_players(actor_address)

    def read_ships(self, actor_address, raw_name):
        """
        Generates a "Ship" object to collect the relevant information about
        a ship actor, then appends a summarized version of that info to
        the self.run_info
        :param actor_address: The memory address which the actor begins at
        :param raw_name: The raw name of the actor
        """
        ship = Ship(self.rm, actor_address, self.my_coords, raw_name)
        ship_info = ship.get_ship_info()
        if ship_info:
            self.run_info.append(ship_info)

    def read_world_players(self, actor_address):
        """
        Reads information about an AthenaPlayerState actor (a server-level
        player object), to obtain info on who is on the server. Append the user
        to the list of players on the server for a given run
        :param actor_address: The memory address which the actor begins at
        """
        player_name_location = self.rm.read_ptr(
            actor_address + OFFSETS.get('APlayerState.PlayerName')
        )
        player_name = self.rm.read_name_string(player_name_location)

        if player_name and player_name not in self.server_players:
            self.server_players.append(player_name)
