import ctypes
import ctypes.wintypes
import psutil
import struct
from string import printable


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
Module32First.argtypes = [ctypes.c_void_p, ctypes.POINTER(MODULEENTRY32) ]
Module32First.rettype = ctypes.c_int

CloseHandle = ctypes.windll.kernel32.CloseHandle
CloseHandle.argtypes = [ctypes.c_void_p]
CloseHandle.rettype = ctypes.c_int

# ReadProcessMemory is also a cytpe, but will perform the actual memory reading
ReadProcessMemory = ctypes.WinDLL('kernel32', use_last_error=True).ReadProcessMemory
ReadProcessMemory.argtypes = [ctypes.wintypes.HANDLE, ctypes.wintypes.LPCVOID,
                              ctypes.wintypes.LPVOID, ctypes.c_size_t,
                              ctypes.POINTER(ctypes.c_size_t)]
ReadProcessMemory.restype = ctypes.wintypes.BOOL


class ReadMemory:
    """
    Class responsible for aiding is memory reading
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
        self.pid = self._get_process_id()
        self.handle = self._get_process_handle()
        self.base_address = self._get_base_address()

    def _get_process_id(self):
        """
        Determines the process ID for the given executable name
        """
        for proc in psutil.process_iter():
            if self.exe in proc.name():
                return proc.pid
        raise Exception(f"Cannot find executable with provided name: {self.exe}")

    def _get_process_handle(self):
        """
        Attempts to open a handle (using read and query permissions only) for
        the class process ID
        :return: an open process handle for our process ID (which matches the
        executable), used to make memory calls
        """
        try:
            return ctypes.windll.kernel32.OpenProcess(PROCESS_QUERY_INFORMATION | PROCESS_VM_READ, False, self.pid)
        except Exception as e:
            raise Exception(f"Cannot create handle for pid {self.pid}: Error: {e}")

    def _get_base_address(self):
        """
        Using the global ctype constructors, determine the base address
        of the process ID we are working with. In something like cheat engine, 
        this is the equivilent of the "SoTGame.exe" portions in 
        "SoTGame.exe"+0x15298A
        :return: the base memory address for the process
        """
        h_module_snap = ctypes.c_void_p(0)
        me32 = MODULEENTRY32()
        me32.dwSize = ctypes.sizeof(MODULEENTRY32)
        h_module_snap = CreateToolhelp32Snapshot(TH32CS_SNAPMODULE | TH32CS_SNAPMODULE32, self.pid)
        ret = Module32First(h_module_snap, ctypes.byref(me32))

        if ret == 0:
            print('Error on Thread32First')
            return False

        ret = Module32First(h_module_snap, ctypes.pointer(me32))
        if ret == 0:
            print('ListProcessModules() Error on Module32First')

        return me32.modBaseAddr

    def read_bytes(self, address:int, byte:int) -> bytes:
        """
        Read a number of bytes at a specific address
        :param address: address at which to read a number of bytes
        :param byte: count of bytes to read
        """
        if not isinstance(address, int):
            raise TypeError('Address must be int: {}'.format(address))
        buff = ctypes.create_string_buffer(byte)
        bytes_read = ctypes.c_size_t()
        ctypes.windll.kernel32.SetLastError(0)
        ReadProcessMemory(self.handle, ctypes.c_void_p(address), ctypes.byref(buff), byte, ctypes.byref(bytes_read))
        error_code = ctypes.windll.kernel32.GetLastError()
        if error_code:
            print("Error")
            ctypes.windll.kernel32.SetLastError(0)
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
        # 4 bytes address
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
        # 8 bytes address
        read_bytes = self.read_bytes(address, struct.calcsize('Q'))
        read_bytes = struct.unpack('<Q', read_bytes)[0]
        return read_bytes

    def read_string(self, address: int, byte=50) -> int:
        """
        Read a number of bytes and convert that to a string up until the first
        occurance of no data. Useful in getting raw names
        :param address: address at which to read a number of bytes
        :param byte: count of bytes to read, optional as we assume a 50
        byte name
        """
        buff = self.read_bytes(address, byte)
        # print(type(buff))
        i = buff.find(b'\x00')
        return str("".join(map(chr, buff[:i])))

    def read_name_string(self, address: int, byte=32) -> int:
        """
        Used to convert bytes that represent a players name to a string. Player
        names always are seperated by at least 3 null characters
        :param address: address at which to read a number of bytes
        :param byte: count of bytes to read, optional as we assume a 32
        byte name
        """
        buff = self.read_bytes(address, byte)
        i = buff.find(b"\x00\x00\x00")
        joined = str("".join(map(chr, buff[:i])))
        return ''.join(char for char in joined if char in printable)
