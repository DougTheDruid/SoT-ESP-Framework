"""
@Author https://github.com/DougTheDruid
@Source https://github.com/DougTheDruid/SoT-ESP-Framework
For community support, please contact me on Discord: DougTheDruid#2784
"""

import pyglet
from pyglet.text import Label
from pyglet.libs.win32 import _gdi32, _dwmapi
from pyglet.libs.win32.types import ctypes, DWORD, BOOL, HRGN
from pyglet.gl import Config, glFlush, glEnable, glBlendFunc, GL_BLEND, \
    GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA
import win32api
import win32con
import win32gui
from helpers import SOT_WINDOW, SOT_WINDOW_H, SOT_WINDOW_W, main_batch
from sot_hack import SoTMemoryReader

# See explanation in Main, toggle for a non-graphical debug
DEBUG = False

# Pyglet clock used to track time via FPS
clock = pyglet.clock.Clock()

# Magic numbers of enabling BlurBehind functionality
DWM_BB_ENABLE = 0x00000001
DWM_BB_BLURREGION = 0x00000002


class DWM_BLURBEHIND(ctypes.Structure):  # pylint: disable=invalid-name
    """
    Replica class of windows DWM_BLURBEHIND
    """
    _fields_ = [
        ("dwFlags", DWORD),
        ("fEnable", BOOL),
        ("hRgnBlur", HRGN),
        ("fTransitionOnMaximized", DWORD),
    ]


def update_transparency():
    """
    Method to enable BlurBehind in a specific region (all of our window), we
    can then use BlurBehind as our Alpha layer
    """
    # Region of all of our window
    region = _gdi32.CreateRectRgn(0, 0, -1, -1)

    # Create out BlurBehind c-type from follow the struct above & set variables
    bb = DWM_BLURBEHIND()
    bb.dwFlags = DWM_BB_ENABLE | DWM_BB_BLURREGION  # pylint: disable=attribute-defined-outside-init, invalid-name
    bb.hRgnBlur = region  # pylint: disable=attribute-defined-outside-init, invalid-name
    bb.fEnable = True  # pylint: disable=attribute-defined-outside-init, invalid-name

    # Enable the BlurBehind for our given window handle
    _dwmapi.DwmEnableBlurBehindWindow(hwnd, ctypes.byref(bb))

    # Delete the region because its no longer needed after setting it up
    _gdi32.DeleteObject(region)


def set_window_info():
    """
    Sets windows attributes for a global hwnd (window ID). Responsible
    for transparency, topmost, and covering our SoT window.
    """
    # Setting attributes for our window to support transparency and
    # click-through
    win32gui.SetWindowLong(hwnd, win32con.GWL_EXSTYLE,
                           win32con.WS_EX_TRANSPARENT |
                           win32con.WS_EX_LAYERED |
                           win32con.WS_EX_TOPMOST)

    # Move the window to cover SoT & keep it on top always
    win32gui.SetWindowPos(hwnd, win32con.HWND_TOPMOST, SOT_WINDOW[0],
                          SOT_WINDOW[1], 0, 0, win32con.SWP_NOSIZE)

    # Set (0, 0, 0) to our alpha color. Not the best, but works for now
    win32gui.SetLayeredWindowAttributes(hwnd, win32api.RGB(0, 0, 0), 254,
                                        win32con.LWA_ALPHA)


def update_all(_):
    """
    Triggers an entire read_actors call in our SoT Memory Reader. Will
    re-populate all of the display objects if something entered the screen
    or render distance.
    """
    smr.read_actors()


def load_graphics(_):
    """
    Our main graphical loop which updates all of our "interesting" items.
    During a "full run" (update_all()), a list of the objects near us and we
    care about is generated. Each of those objects has a ".update()" method
    we use to re-poll data for that item (required per display_object.py)
    """
    # Update our players coordinate information
    smr.update_my_coords()

    # Initialize a list of items which are no longer valid in this loop
    to_remove = []

    # For each actor that is stored from the most recent run of read_actors
    for actor in smr.display_objects:
        # Call the update function within the actor object
        actor.update(smr.my_coords)

        # If the actor isn't the actor we expect (per .update), prepare to nuke
        if actor.to_delete:
            to_remove.append(actor)

    # Clean up any items which arent valid anymore
    for removable in to_remove:
        smr.display_objects.remove(removable)


if __name__ == '__main__':
    # Initialize our SoT Hack object, and do a first run of reading actors
    smr = SoTMemoryReader()
    smr.read_actors()

    # Custom Debug mode for using a literally python interpreter debugger
    # to validate our fields.
    if DEBUG:
        while True:
            smr.read_actors()

    # Create a window config with an alpha size to 8 bytes, allows transparency
    # Interesting additional config options: double_buffer=False, vsync=False
    config = Config(alpha_size=8)
    # Create a borderless window with Pyglet at the same size as our SoT Window
    window = pyglet.window.Window(SOT_WINDOW_W, SOT_WINDOW_H,
                                  vsync=False, style='borderless',
                                  config=config)
    hwnd = window._hwnd  # pylint: disable=protected-access

    # Update the window we created to be transparent, have click-through
    # capabilities, etc.
    set_window_info()

    @window.event
    def on_draw():
        """
        The event which our window uses to determine what to draw on the
        screen. First clears the screen, then updates our player count, then
        draws both our batch (think of a canvas) & fps display
        """
        window.clear()

        # Update our player count Label & player list
        player_count.text = f"Player Count: {len(smr.server_players)}"
        # player_list.text = "\n".join(smr.server_players)

        # Draw our main batch & FPS counter at the bottom left
        main_batch.draw()
        fps_display.draw()

        # Make the background transparent and flush openGL
        update_transparency()
        glFlush()

    # We schedule an "update all" to scan all actors every 5seconds
    pyglet.clock.schedule_interval(update_all, 5)

    # We schedule a check to make sure the game is still running every 3 seconds
    pyglet.clock.schedule_interval(smr.rm.check_process_is_active, 3)

    # We schedule an basic graphics load which is responsible for drawing
    # our interesting information to the screen. Max 144fps, can set unlimited
    # pyglet.clock.schedule(load_graphics)
    pyglet.clock.schedule_interval(load_graphics, 1/144)

    # Adds an FPS counter at the bottom left corner of our pyglet window
    # Note: May not translate to actual FPS, but rather FPS of the program
    fps_display = pyglet.window.FPSDisplay(window)

    # Enable blending & background alpha functionality
    glEnable(GL_BLEND)
    glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)

    # Our base player_count label in the top-right of our screen. Updated
    # in on_draw()
    player_count = Label("Player Count: {}",
                         x=SOT_WINDOW_W * 0.85,
                         y=SOT_WINDOW_H * 0.9, batch=main_batch)

    # The label for showing all players on the server under the count
    if False:  # pylint: disable=using-constant-test
        player_list = Label("\n".join(smr.server_players), x=SOT_WINDOW_W * 0.85,
                            y=(SOT_WINDOW_H-25) * 0.9, batch=main_batch, width=300,
                            multiline=True)
        # Note: The width of 300 is the max pixel width of a single line
        # before auto-wrapping the text to the next line. Updated in on_draw()

    # Runs our application and starts to use our scheduled events to show data
    pyglet.app.run()
    # Note - ***Nothing past here will execute as app.run() is a loop***
