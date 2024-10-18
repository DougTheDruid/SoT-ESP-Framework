"""
@Author https://github.com/DougTheDruid
@Source https://github.com/DougTheDruid/SoT-ESP-Framework
For community support, please contact me on Discord: DougTheDruid#2784
"""
from base64 import b64decode
import pyglet
from pyglet.text import Label
from pyglet.gl import Config
from helpers import SOT_WINDOW, SOT_WINDOW_H, SOT_WINDOW_W, main_batch, \
    version, logger, initialize_window
from sot_hack import SoTMemoryReader


# The FPS __Target__ for the program.
FPS_TARGET = 60

# See explanation in Main, toggle for a non-graphical debug
DEBUG = False

# Pyglet clock used to track time via FPS
clock = pyglet.clock.Clock()


def generate_all(_):
    """
    Triggers an entire read_actors call in our SoT Memory Reader. Will
    re-populate all of the display objects if something entered the screen
    or render distance.
    """
    smr.read_actors()


def update_graphics(_):
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

    # Clean up any items which aren't valid anymore
    for removable in to_remove:
        smr.display_objects.remove(removable)


if __name__ == '__main__':
    logger.info(
        b64decode("RG91Z1RoZURydWlkJ3MgRVNQIEZFrYW1ld29yayBTdGFydGluZw==").decode("utf-8")
    )
    logger.info(f"Hack Version: {version}")

    # Initialize our SoT Hack object with error handling
    try:
        smr = SoTMemoryReader()
        if not smr.is_initialized:  # Check if the reader initialized correctly
            raise Exception("Memory reader failed to initialize. Please check the target process.")
    except Exception as e:
        logger.error(f"Error initializing SoTMemoryReader: {e}")
        exit(1)  # Exit the program if initialization fails

    # Custom Debug mode for using a literal python interpreter debugger
    # to validate our fields. Does not generate a GUI.
    if DEBUG:
        while True:
            smr.read_actors()

    # You may want to add/modify this custom config per the pyglet docs to
    # disable vsync or other options: https://tinyurl.com/45tcx6eu
    config = Config(double_buffer=True, depth_size=24, alpha_size=8)

    # Create an overlay window with Pyglet at the same size as our SoT Window
    window = pyglet.window.Window(SOT_WINDOW_W, SOT_WINDOW_H,
                                  vsync=False, style='overlay', config=config,
                                  caption="DougTheDruid's ESP Framework")
    hwnd = window._hwnd  # pylint: disable=protected-access

    # Move our window to the same location that our SoT Window is at
    window.set_location(SOT_WINDOW[0], SOT_WINDOW[1])

    @window.event
    def on_draw():
        """
        The event which our window uses to determine what to draw on the
        screen. First clears the screen, then updates our player count, then
        draws both our batch (think of a canvas) & fps display
        """
        window.clear()

        # Update our player count Label & crew list
        if smr.crew_data:
            player_count.text = f"Player Count: {smr.crew_data.total_players}"
            # crew_list.text = smr.crew_data.crew_str

        # Draw our main batch & FPS counter at the bottom left
        main_batch.draw()
        fps_display.draw()

    # Initializing the window for writing
    init = initialize_window()

    # We schedule an "update all" to scan all actors every 5 seconds
    pyglet.clock.schedule_interval(generate_all, 5)

    # We schedule a check to make sure the game is still running every 3 seconds
    pyglet.clock.schedule_interval(smr.rm.check_process_is_active, 3)

    # We schedule a basic graphics load which is responsible for updating
    # the actors we are interested in (from our generate_all). Runs as fast as possible
    pyglet.clock.schedule(update_graphics)

    # Adds an FPS counter at the bottom left corner of our pyglet window
    # Note: May not translate to actual FPS, but rather FPS of the program
    fps_display = pyglet.window.FPSDisplay(window)

    # Our base player_count label in the top-right of our screen. Updated
    # in on_draw(). Use a default of "Initializing", which will update once the
    # hack is actually running
    player_count = Label("...Initializing Framework...",
                         x=SOT_WINDOW_W * 0.85,
                         y=SOT_WINDOW_H * 0.9, batch=main_batch)

    # The label for showing all players on the server under the count
    # This purely INITIALIZES it does not inherently update automatically
    if False:  # pylint: disable=using-constant-test
        crew_list = Label("", x=SOT_WINDOW_W * 0.85,
                          y=(SOT_WINDOW_H - 25) * 0.9, batch=main_batch, width=300,
                          multiline=True)
        # Note: The width of 300 is the max pixel width of a single line
        # before auto-wrapping the text to the next line. Updated in on_draw()

    # Runs our application, targeting a specific refresh rate (1/60 = 60fps)
    pyglet.app.run(interval=1 / FPS_TARGET)
    # Note - ***Nothing past here will execute as app.run() is a loop***
