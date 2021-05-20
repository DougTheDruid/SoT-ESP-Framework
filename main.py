"""
@Author https://github.com/DougTheDruid
@Source https://github.com/DougTheDruid/SoT-ESP-Framework
For community support, please join our Discord: https://discord.gg/2rRvQjhg7n
"""


from SoTHack import SoTMemoryReader
import pygame
from PyGameHelper import PyGameHelper, fuchsia

DEBUG = False

if __name__ == '__main__':
    # Initialize our SoT Hack object, and do a first run of reading actors
    smr = SoTMemoryReader()
    done = False
    loops = []
    smr.read_actors()

    # We only want to make the PyGame resources if we aren't running in Debug
    # mode (otherwise we will get a black screen during debug)
    if not DEBUG:
        pgh = PyGameHelper()

    # Our pygame loop that is responsible for actually display object if we
    # are in debug mode, doesnt push graphics to pygame, just reads actor data
    while not done:
        smr.read_actors()

        if not DEBUG:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    done = True

        if not DEBUG:
            # Fill the screen with the transparent color we set in PyGameHelper
            pgh.screen.fill(fuchsia)

            # If there is actor data from read_actors(), display the info
            # to screen
            if smr.run_info:
                for actor in smr.run_info:
                    screen = actor.get('Screen_Coordinates')
                    pygame.draw.circle(pgh.screen, actor.get('Color'),
                                       screen, 10)
                    pgh.screen.blit(actor.get('Text'),
                                    (screen[0]+13, screen[1]-10))

            # If there is data about the worlds players, display play names
            # and count in a list on the screen
            if smr.server_players:
                count = len(smr.server_players)
                player_total = pgh.my_font.render(f"Count: {count}", False,
                                                  (109, 89, 148))
                pgh.screen.blit(player_total, (2300, 100-25))
                if False:
                    for player in range(0, count):
                        player_text = pgh.my_font.render(
                            f"{smr.server_players[player]}",
                            False, (109, 89, 148)
                        )
                        pgh.screen.blit(player_text, (2300, 100+(player*25)))

            pygame.display.update()
