"""
@Author https://github.com/DougTheDruid
@Source https://github.com/DougTheDruid/SoT-ESP-Framework
"""

from string import printable
from helpers import logger
import ctypes
import ctypes.wintypes
import struct
import psutil
import re


MAX_PATH = 260
MAX_MODULE_NAME32 = 255
TH32CS_SNAPMODULE = 0x00000009
TH32CS_SNAPMODULE32 = 0x00000011
PROCESS_QUERY_INFORMATION = 0x0400
PROCESS_VM_READ = 0x0010


# ModuleEntry32, CreateToolhelp32Snapshot, and Module32First are ctypes which
# helps us identify the base address for the game in memory. We then use
# that base address to build off of
class MODULEENTRY32(ctypes.Structure):
    """
    Windows C-type ModuleEntry32 object used to interact with our game process
    """
    _fields_ = [('dwSize', ctypes.c_ulong),
                ('th32ModuleID', ctypes.c_ulong),
                ('th32ProcessID', ctypes.c_ulong),
                ('GlblcntUsage', ctypes.c_ulong),
                ('ProccntUsage', ctypes.c_ulong),
                ('modBaseAddr', ctypes.c_size_t),
                ('modBaseSize', ctypes.c_ulong),
                ('hModule', ctypes.c_void_p),
                ('szModule', ctypes.c_char * (MAX_MODULE_NAME32+1)),
                ('szExePath', ctypes.c_char * MAX_PATH)]


CreateToolhelp32Snapshot = ctypes.windll.kernel32.CreateToolhelp32Snapshot
CreateToolhelp32Snapshot.reltype = ctypes.c_long
CreateToolhelp32Snapshot.argtypes = [ctypes.c_ulong, ctypes.c_ulong]

Module32First = ctypes.windll.kernel32.Module32First
Module32First.argtypes = [ctypes.c_void_p, ctypes.POINTER(MODULEENTRY32)]
Module32First.rettype = ctypes.c_int

Module32Next = ctypes. windll.kernel32.Module32Next
Module32Next.argtypes = [ctypes. c_void_p, ctypes.POINTER(MODULEENTRY32)]
Module32Next.rettype = ctypes.c_int

CloseHandle = ctypes.windll.kernel32.CloseHandle
CloseHandle.argtypes = [ctypes.c_void_p]
CloseHandle.rettype = ctypes.c_int

GetLastError = ctypes.windll.kernel32.GetLastError
GetLastError.rettype = ctypes.c_long

# ReadProcessMemory is also a cytpe, but will perform the actual memory reading
ReadProcessMemory = ctypes.WinDLL(
    'kernel32', use_last_error=True
).ReadProcessMemory
ReadProcessMemory.argtypes = [ctypes.wintypes.HANDLE, ctypes.wintypes.LPCVOID,
                              ctypes.wintypes.LPVOID, ctypes.c_size_t,
                              ctypes.POINTER(ctypes.c_size_t)]
ReadProcessMemory.restype = ctypes.wintypes.BOOL

UWORLDPATTERN = "48 8B 05 ? ? ? ? 48 8B 88 ? ? ? ? 48 85 C9 74 06 48 8B 49 70"
GOBJECTPATTERN = "89 0D ? ? ? ? 48 8B DF 48 89 5C 24"
GNAMEPATTERN = "48 8B 1D ? ? ? ? 48 85 DB 75 ? B9 08 04 00 00"


def convert_pattern_to_regex(pattern: str) -> bytes:
    """
    Taking in our standard "pattern" format, convert that format to one that
    can be used in a regex search for those bytes
    :param pattern: the raw string-formatted pattern we want to convert
    :return: Regex-compatible bytes pattern search
    """
    split_bytes = pattern.split(' ')
    re_pat = bytearray()
    for byte in split_bytes:
        if '?' in byte:
            re_pat.extend(b'.')
        else:
            re_pat.extend(re.escape(bytes.fromhex(byte)))
    return bytes(re_pat)


def search_data_for_pattern(data: bytes, raw_pattern: str):
    """
    Convert out raw pattern into an address where that pattern exists in
    memory
    :param data: A large dump of the early process memory
    :param raw_pattern: string-formatted pattern we want to identify the
    location of in memory
    :return: Return the first location of our pattern in the large data scan we
    conducted at memory reader init time.
    """
    return re.search(
        convert_pattern_to_regex(raw_pattern),
        data,
        re.MULTILINE | re.DOTALL
    ).start()


class ReadMemory:
    """
    Class responsible for aiding in memory reading
    """
    def __init__(self, exe_name: str):
        """
        Gets the process ID for the executable, then a handle for that process,
        then we get the base memory address for our process using the handle.

        With the base memory address known, we can then perform our standard
        memory calls (read_int, etc) to get data from memory.

        :param exe_name: The executable name of the program we want to read
        memory from
        """
        self.exe = exe_name
        try:
            self.pid = self._get_process_id()
            self.handle = self._get_process_handle()
            self.base_address = self._get_base_address()

            # There is definitely a better way to get lots of base memory data, but
            # this is v1 of automated pattern searching
            bulk_scan = self.read_bytes(self.base_address, 1000000000)
            self.u_world_base = search_data_for_pattern(bulk_scan, UWORLDPATTERN)
            self.g_object_base = search_data_for_pattern(bulk_scan, GOBJECTPATTERN)
            self.g_name_base = search_data_for_pattern(bulk_scan, GNAMEPATTERN)
            del bulk_scan

            logger.info(f"gObject offset: {hex(self.g_object_base)}")
            logger.info(f"uWorld offset: {hex(self.u_world_base)}")
            logger.info(f"gName offset: {hex(self.g_name_base)}")
        except Exception as e:
            logger.error(f"Error initializing memory reader")

    def _get_process_id(self):
        """
        Determines the process ID for the given executable name
        """
        for proc in psutil.process_iter():
            if self.exe in proc.name():
                return proc.pid
        raise Exception(f"Cannot find executable with name: {self.exe}")

    def _get_process_handle(self):
        """
        Attempts to open a handle (using read and query permissions only) for
        the class process ID
        :return: an open process handle for our process ID (which matches the
        executable), used to make memory calls
        """
        try:
            return ctypes.windll.kernel32.OpenProcess(PROCESS_QUERY_INFORMATION
                                                      | PROCESS_VM_READ,
                                                      False, self.pid)
        except Exception as e:
            raise Exception(f"Cannot create handle for pid {self.pid}: "
                            f"Error: {str(e)}")

    def _get_base_address(self):
        """
        Using the global ctype constructors, determine the base address
        of the process ID we are working with. In something like cheat engine,
        this is the equivalent of the "SoTGame.exe" portions in
        "SoTGame.exe"+0x15298A. Creates a snapshot of the process, then begins
        to iterate over the modules (.exe/.dlls) until we match the provided
        exe_name
        :return: the base memory address for the process
        """
        h_module_snap = ctypes.c_void_p(0)
        me32 = MODULEENTRY32()
        me32.dwSize = ctypes.sizeof(MODULEENTRY32)  # pylint: disable=invalid-name, attribute-defined-outside-init
        h_module_snap = CreateToolhelp32Snapshot(TH32CS_SNAPMODULE, self.pid)

        mod = Module32First(h_module_snap, ctypes.pointer(me32))

        if not mod:
            CloseHandle(h_module_snap)
            raise Exception(f"Error getting {self.exe} base address: {GetLastError()}")
        while mod:
            if me32.szModule.decode() == self.exe:
                CloseHandle(h_module_snap)
                return me32.modBaseAddr
            mod = Module32Next(h_module_snap, ctypes.pointer(me32))

    def check_process_is_active(self, _):
        """
        Check if the game is still running and if not, exit
        """
        if not self._process_is_active():
            logger.info(f"Appears {self.exe} has been closed. Exiting program.")
            exit(0)

    def _process_is_active(self) -> bool:
        """
        Check if the PID of the game exists
        :return: value indicating the game process is alive or not
        """
        return psutil.pid_exists(self.pid)

    def read_bytes(self, address: int, byte: int) -> bytes:
        """
        Read a number of bytes at a specific address
        :param address: address at which to read a number of bytes
        :param byte: count of bytes to read
        """
        if not isinstance(address, int):
            raise TypeError('Address must be int: {}'.format(address))
        buff = ctypes.create_string_buffer(byte)
        bytes_read = ctypes.c_size_t()
        ReadProcessMemory(self.handle, ctypes.c_void_p(address),
                          ctypes.byref(buff), byte, ctypes.byref(bytes_read))
        raw = buff.raw
        return raw

    def read_int(self, address: int):
        """
        :param address: address at which to read a number of bytes
        """
        read_bytes = self.read_bytes(address, struct.calcsize('i'))
        read_bytes = struct.unpack('<i', read_bytes)[0]
        return read_bytes

    def read_float(self, address: int) -> float:
        """
        Read the float (4 bytes) at a given address and return that data
        :param address: address at which to read a number of bytes
        """
        read_bytes = self.read_bytes(address, struct.calcsize('f'))
        read_bytes = struct.unpack('<f', read_bytes)[0]
        return read_bytes

    def read_ulong(self, address: int):
        """
        Read the uLong (4 bytes) at a given address and return that data
        :param address: address at which to read a number of bytes
        :return: the 4-bytes of data (ulong) that live at the provided
        address
        """
        read_bytes = self.read_bytes(address, struct.calcsize('L'))
        read_bytes = struct.unpack('<L', read_bytes)[0]
        return read_bytes

    def read_ptr(self, address: int) -> int:
        """
        Read the uLongLong (8 bytes) at a given address and return that data
        :param address: address at which to read a number of bytes
        :return: the 8-bytes of data (ulonglong) that live at the provided
        address
        """
        read_bytes = self.read_bytes(address, struct.calcsize('Q'))
        read_bytes = struct.unpack('<Q', read_bytes)[0]
        return read_bytes

    def read_string(self, address: int, byte: int = 50) -> int:
        """
        Read a number of bytes and convert that to a string up until the first
        occurrence of no data. Useful in getting raw names
        :param address: address at which to read a number of bytes
        :param byte: count of bytes to read, optional as we assume a 50
        byte name
        """
        buff = self.read_bytes(address, byte)
        i = buff.find(b'\x00')
        return str("".join(map(chr, buff[:i])))

    def read_name_string(self, address: int, byte: int = 32) -> str:
        """
        Used to convert bytes that represent a players name to a string. Player
        names always are separated by at least 3 null characters
        :param address: address at which to read a number of bytes
        :param byte: count of bytes to read, optional as we assume a 32
        byte name
        """
        buff = self.read_bytes(address, byte)
        i = buff.find(b"\x00\x00\x00")
        joined = str("".join(map(chr, buff[:i])))
        return ''.join(char for char in joined if char in printable)
