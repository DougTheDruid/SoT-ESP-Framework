"""
@Author https://github.com/DougTheDruid
@Source https://github.com/DougTheDruid/SoT-ESP-Framework
For community support, please contact me on Discord: DougTheDruid#2784
"""

from sot_hack import SoTMemoryReader
import pyglet
from pyglet import shapes
from pyglet.text import Label
import win32api
import win32con
import win32gui
from helpers import SOT_WINDOW, SOT_WINDOW_H, SOT_WINDOW_W, main_batch

NOSIZE = 1

# See explination in Main
DEBUG = False

# Stores our display objects, making them non-localized so Pyglet can see them
cache = []

# Creating a Pyglet clock and Batch to more efficiently draw
clock = pyglet.clock.Clock()


def set_window_info():
    # Setting attribs. for our window to support transparency and click-through
    win32gui.SetWindowLong(hwnd, win32con.GWL_EXSTYLE,
                           win32con.WS_EX_TRANSPARENT |
                           win32con.WS_EX_LAYERED |
                           win32con.WS_EX_TOPMOST)

    # Move the window to cover SoT
    win32gui.SetWindowPos(hwnd, win32con.HWND_TOPMOST, SOT_WINDOW[0],
                          SOT_WINDOW[1], 0, 0, NOSIZE)

    # Set window transparency color
    win32gui.SetLayeredWindowAttributes(hwnd, win32api.RGB(0, 0, 0), 255,
                                        win32con.LWA_COLORKEY)


def update_all(_):
    """
    Triggers an entire read_actors call in our SoT Memory Reader. Will
    re-populate all of the display objects if something entered the screen
    or render distance. Not actually responisble for displaying anything to
    the screen
    """
    smr.read_actors()


def load_graphics(_):
    """
    Our main graphical loop which updates all of our "interesting" items
    """
    global cache

    # Responsible for cleaning up old "Label" objects which we created
    # Necessary until we determine a better path forward
    for cached_item in cache:
        try:
            cached_item.delete()
        except:
            continue

    # Update our players coordinate information
    smr.update_my_coords()
    to_remove = []

    # For each actor that is stored from the most recent run of read_actors
    for actor in smr.display_objects:
        # Call the update function within the actor object
        actor.update(smr.my_coords)

        # If the actor isnt the actor we expect (per update()), remove it
        if actor.to_delete:
            to_remove.append(actor)

    # Clean up any items which arent valid anymore
    for removable in to_remove:
        smr.display_objects.remove(removable)


if __name__ == '__main__':
    # Initialize our SoT Hack object, and do a first run of reading actors
    smr = SoTMemoryReader()
    smr.read_actors()

    # Custom Debug mode for using a literaly python interpretter debugger
    # to validate our fields.
    if DEBUG:
        while True:
            smr.read_actors()

    # Create a borderless window with Pyglet at the same size as our SoT Window
    window = pyglet.window.Window(SOT_WINDOW_W, SOT_WINDOW_H,
                                  vsync=False, style='borderless')
    hwnd = window._hwnd

    # Update the window we created to be transparent, have click-through
    # capabilities, etc.
    set_window_info()

    # The event which our window uses to determine what to draw to the screen
    @window.event
    def on_draw():
        window.clear()
        player_count.text = f"Player Count: {len(smr.server_players)}"
        main_batch.draw()
        fps_display.draw()

    # We schedule an "update all" to scan all actors every 5seconds
    pyglet.clock.schedule_interval(update_all, 5)

    # We schedule an basic graphics load which is responsible for drawing
    # our interesting information to the screen
    pyglet.clock.schedule(load_graphics)

    # Adds an FPS counter at the botton left corner of our pyglet window
    # Note: May not translate to actual FPS, but rather FPS of the program
    fps_display = pyglet.window.FPSDisplay(window)

    # Our base player_count label in the top-right of our screen
    player_count = Label("Player Count: {}",
                         x=SOT_WINDOW_W * 0.85,
                         y=SOT_WINDOW_H * 0.9, batch=main_batch)

    if False:
        player_list = Label("\n".join(smr.server_players), x=SOT_WINDOW_W * 0.85,
                            y=(SOT_WINDOW_H-25) * 0.9, batch=main_batch, width=32,
                            multiline=True)

    # Runs our application and starts to use our scheduled events to
    # build/show data
    pyglet.app.run()
