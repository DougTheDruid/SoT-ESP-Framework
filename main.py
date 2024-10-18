from base64 import b64decode
import pyglet
import argparse
from pyglet.text import Label
from pyglet.gl import Config
from helpers import SOT_WINDOW, SOT_WINDOW_H, SOT_WINDOW_W, main_batch, \
    version, logger, initialize_window
from sot_hack import SoTMemoryReader

# Command-line argument parsing for better control over debug and fps settings
parser = argparse.ArgumentParser(description='ESP Framework for SoT')
parser.add_argument('--fps', type=int, default=60, help='Target FPS for the program')
parser.add_argument('--debug', action='store_true', help='Enable debug mode')
args = parser.parse_args()

# The FPS __Target__ for the program, adjustable via command-line argument
FPS_TARGET = args.fps

# Debug flag controlled via command-line argument
DEBUG = args.debug

# Pyglet clock used to track time via FPS
clock = pyglet.clock.Clock()

def generate_all(_):
    """
    Triggers an entire read_actors call in our SoT Memory Reader. Will
    re-populate all of the display objects if something entered the screen
    or render distance.
    """
    try:
        smr.read_actors()
    except Exception as e:
        logger.error(f"Error reading actors: {e}")

def update_graphics(_):
    """
    Main graphical loop to update all interesting items.
    Each object in smr.display_objects has an .update() method to refresh its data.
    """
    try:
        smr.update_my_coords()
        to_remove = []

        # Update each actor and mark those to be removed
        for actor in smr.display_objects:
            actor.update(smr.my_coords)
            if actor.to_delete:
                to_remove.append(actor)

        # Remove invalid actors
        for removable in to_remove:
            smr.display_objects.remove(removable)
    except Exception as e:
        logger.error(f"Error updating graphics: {e}")

if __name__ == '__main__':
    logger.info(
        b64decode("RG91Z1RoZURydWlkJ3MgRVNQIEZyYW1ld29yayBTdGFydGluZw==").decode("utf-8")
    )
    logger.info(f"Hack Version: {version}")

    # Initialize SoT Hack object and do the first run of reading actors
    smr = SoTMemoryReader()

    # Debug mode bypasses the GUI and runs the reading process in a loop
    if DEBUG:
        logger.info("Running in Debug mode. No graphical interface will be displayed.")
        while True:
            try:
                smr.read_actors()
            except Exception as e:
                logger.error(f"Error in Debug mode: {e}")
    else:
        # Set pyglet window config, can modify vsync and other options here
        config = Config(double_buffer=True, depth_size=24, alpha_size=8)
        window = pyglet.window.Window(SOT_WINDOW_W, SOT_WINDOW_H,
                                      vsync=False, style='overlay', config=config,
                                      caption="DougTheDruid's ESP Framework")
        hwnd = window._hwnd  # pylint: disable=protected-access
        window.set_location(SOT_WINDOW[0], SOT_WINDOW[1])

        @window.event
        def on_draw():
            """
            Window event to draw content. Updates player count and draws the batch & FPS display.
            """
            window.clear()
            if smr.crew_data:
                player_count.text = f"Player Count: {smr.crew_data.total_players}"
            main_batch.draw()
            fps_display.draw()

        # Initialize the window
        init = initialize_window()

        # Schedule actor update every 5 seconds and process check every 3 seconds
        pyglet.clock.schedule_interval(generate_all, 5)
        pyglet.clock.schedule_interval(smr.rm.check_process_is_active, 3)

        # Schedule continuous graphics updates as fast as possible
        pyglet.clock.schedule(update_graphics)

        # Add FPS counter to the window
        fps_display = pyglet.window.FPSDisplay(window)

        # Initialize player count label
        player_count = Label("...Initializing Framework...",
                             x=SOT_WINDOW_W * 0.85,
                             y=SOT_WINDOW_H * 0.9, batch=main_batch)

        # Run the application with a specified FPS target
        pyglet.app.run(interval=1/FPS_TARGET)
