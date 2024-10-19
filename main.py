from base64 import b64decode
import pyglet
from pyglet.text import Label
from pyglet.gl import Config
from helpers import SOT_WINDOW, SOT_WINDOW_H, SOT_WINDOW_W, main_batch, \
    version, logger, initialize_window
from sot_hack import SoTMemoryReader

FPS_TARGET = 60
DEBUG = False

clock = pyglet.clock.Clock()

def generate_all(_):
    smr.read_actors()

def update_graphics(_):
    smr.update_my_coords()
    to_remove = []
    for actor in smr.display_objects:
        actor.update(smr.my_coords)
        if actor.to_delete:
            to_remove.append(actor)
    for removable in to_remove:
        smr.display_objects.remove(removable)

if __name__ == '__main__':
    logger.info(
        b64decode("RG91Z1RoZURydWlkJ3MgRVNQIEZyYW1ld29yayBTdGFydGluZw==").decode("utf-8")
    )
    logger.info(f"Hack Version: {version}")

    smr = SoTMemoryReader()

    if DEBUG:
        while True:
            smr.read_actors()

    config = Config(double_buffer=True, depth_size=24, alpha_size=8)

    window = pyglet.window.Window(SOT_WINDOW_W, SOT_WINDOW_H, vsync=False, config=config,
                                  caption="DougTheDruid's ESP Framework")
    hwnd = window._hwnd  # pylint: disable=protected-access

    window.set_location(SOT_WINDOW[0], SOT_WINDOW[1])

    @window.event
    def on_draw():
        window.clear()

        if smr.crew_data:
            player_count.text = f"Player Count: {smr.crew_data.total_players}"

        main_batch.draw()
        fps_display.draw()

    @window.event
    def on_close():
        pyglet.app.exit()

    init = initialize_window()

    pyglet.clock.schedule_interval(generate_all, 5)
    pyglet.clock.schedule_interval(smr.rm.check_process_is_active, 3)
    pyglet.clock.schedule(update_graphics)

    fps_display = pyglet.window.FPSDisplay(window)

    player_count = Label("...Initializing Framework...",
                         x=SOT_WINDOW_W * 0.85,
                         y=SOT_WINDOW_H * 0.9, batch=main_batch)

    if smr.crew_data:
        crew_list = Label("", x=SOT_WINDOW_W * 0.85,
                          y=(SOT_WINDOW_H-25) * 0.9, batch=main_batch, width=300,
                          multiline=True)

    pyglet.app.run(interval=1/FPS_TARGET)
