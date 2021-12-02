# Doug's Python SoT ESP Framework
Hello all! This is a framework to develop an SoT ESP Hack, all utilizing Python. This is a trimmed down version 
of a personal creation I utilize actively. This is a great foundation for someone who is looking to get started in 
ESP hacks for Sea of Thieves and maybe even other UE4 games! The code should be loaded with comments to help you grasp the "how" and "why" of basic 
memory editing and data display with Python. While this is intended for use within Sea of Thieves specifically, there is a lot
of resources utilized which could be useful in memory reading/editing for almost any game/program.

This hack has the following implemented:
- Get the location of ships in render distance and display them on screen
- Display a count of the players on the server
- Display a list of all players on the server

This is intentionally left as a framework and not a full-featured hack for a few reasons:
1. I already did the hard work of converting C functions to Python for you
2. I don't believe a fully-functioning hand-out would help progress the skill level of programmers
3. Much of the code is very well documented to help you understand the "how" of the hacks inner workings; as a 
   result many resources on hacking forums will give you guidelines for implementing new functionality; I did it myself, 
   you can to
4. I have undergone 6 or 7 major iterations of this same code. **I am still learning** and re-writing functionality all 
   the time; a smaller code base is much more simple to maintain
   
I do ask that if you decided to take this into your own personal development, encourage others to think for themselves a
bit as well and try to maintain a "documentation-focused" mindset as I have. I request that you do not use this 
framework for any commercial purposes (selling "your" version which is based on this framework) without contacting me and
receiving my approval prior.

### Does this work with both Steam & Microsoft versions?
This hack will work with both versions of the game (Microsoft & Steam), and by default is configured to work for the 
Microsoft version. If you are using the Steam version, you will need to change the appropriate variable at the top
of SoTHack.py

### What SoT Version is the framework build for?
Currently, the framework is build for SoT 2.4.0. I attempt to update ASAP, in the event it is not
up-to-date, you will need to modify the global offsets (per "How to update for new SoT Versions"), 
and possibly update your offsets. See "Other Offerings"

### Why Python?!
Python is at its more user-friendly version of C. Hypothetically, we can perform any C action using python,
but make it more readable and beginner-friendly. I am also much more comfortable developing in Python and saw this as
an opportunity to challenge myself.

### Prerequisites
In theory, all you need to get started in using this hack is Python 3.7.9 (have also verified in 3.9.6), and to install 
the requirement found in the requirements.txt. The base framework should automatically create an overlay over your SoT window, 
regardless of size. You MAY need to make some minor changes in the code to accommodate your display configuration 
(helpers.py, top of file). I personally run all of my Python from PyCharm, and start/stop the code execution 
through the built-in Run and Stop functionality. You may choose to implement proper "closing" functionality using pyglet. 

***As a test of faith, to get this code fully-functional you must modify one line of code, remove another entirely, 
and uncomment a third line. This is a VERY small countermeasure to ensure this framework is actually used as intended.***

### How to execute
At the time of writing, the script is built for a version of SoT with ~6 weeks left in Season 3 and given you have the
necessary pre-requisites, should execute with no major issues. Simply run `main.py` once you are in a server.

### How to update for new SoT Versions
The Framework can automatically detect changes in the uWorld, gName, and gObject offsets if there are new version of the game. If for some reason you need to manually override those
found automatically, here is the procedure to do so:
If there has been a game version update:
   1. Load into a game server
   2. Open Cheat Engine 
   3. Open the `SoTGame.exe` process in Cheat Engine
   4. Change your "value type" to an "Array of byte"
   5. One-by-one enter the *patterns* found at the top of `memory_helper.py` (uWorld, gName, gObject) 
   6. Hit scan. Upon scanning, you should get one or two results, he top result is the one we want
   7. Extend the "Address" column to see all the data. Anything after "SoTGame.exe+" is our base offset
   8. Update the relevant variable(s) in the initialization of `ReadMemory`

If the automatically generated offsets match the ones you find in Cheat Engine, and it still is not working, you may also need to update offsets found in the 
`offsets.json` file. If so, update the offsets according to the latest SDK (various providers avaliable on Unknown Cheats, or [try mine if its up to date](https://github.com/DougTheDruid/SoT-Python-Offset-Finder/tree/main/SDK)). You may also use [my offset
finder](https://github.com/DougTheDruid/SoT-Python-Offset-Finder) to help pull the appropriate data from the SDK files

Running the script in Debug mode (set `debug`=`True` in `main.py` and utilize PyCharms Debug feature), may help you 
identify what offsets are *not* working correctly and need updating.

Note: There are some offsets hardcoded into the program, it is possible those hardcoded offsets CAN change and cause
your issues.

### cAn i GeT bAnNeD?!
TL;DR: Yes. You _can_ get banned, such is the risk of cheating.

Longer version: As is, this code purely utilizes a read-only state for the computer's memory. With hundreds of hours utilizing these same read-only permissions, I have never been
banned, nor concerned for being banned. Does that guarantee you won't be? No. Does that guarantee you won't change something (like trying to write memory) that will cause you to 
get banned? No. If you aren't sure what something does, or why something is done a certain way, do some research on the potential impact of changing it before actually changing it. 

### Can you help me implement X feature?
No. I learned to utilize already posted questions/comments easily found online, you can as well. This framework is meant for people who want to put in the work and learn something, 
not receive a hand-out. You also may be able to see the FAQ.md for some useful information.
For community support, please contact me on Discord: DougTheDruid#2784

### How it works
When running `main.py`, an `SoTMemoryReader` object is created (found in `sot_hack.py`). That object creates a 
`ReadMemory` object (found in `memory_helper.py`) which is used to perform our requisite memory calls. We also create
a Pyglet window to display our data, and give Pyglet a set of instructions to run certain
update methods every so often (or every frame).

The `SoTMemoryReader` object gets data about the game world, but has a main game loop function called `read_actors`.
This method is responsible for determining how many actors there are, and reading data about all of those actors. For 
actors' we are interested in knowing more about, we create a relevant class-object to track their information. We also
use that object to build display information for Pyglet to utilize. 

Largely speaking, if you want to see the flow of the code, start at `main.py` and work your way down into the objects
and other files.

Debugging and error information will be available in the `DougsESP.log` file upon running the main.py file.

### Modules
Generally speaking, in my personal version of this framework, I create a separate "Module" to plug into
my hack similarly to how a `Ship` object is created in the framework. This allows me to have all unique logic to parse
data for a given entity type in one location. I recommend using this strategy as it helps keep your `sot_hack.py` file clean, but
also allows you to copy/paste another similar module to use as a starting point when adding new entities.

When using another module as a starting point, you are required to include an `update` method which is called in our
`main.py` to ensure we keep our entity information up-to-date in between scans of the entire actor list. There is
a number of important logic in the update method for `ship.py` to ensure the entities change visibility correctly & are deleted
correctly if something changes unexpectedly.

### Structs
Instead of rebuilding structures similarly to how you would in C or C++, I utilize something fairly frequently in my
code that may not be very clear called `struct`. This is a Python-native import which allows us to more easily convert
hex data to a list of information.

Generally, I read a number of bytes at a memory location given what I want to grab, then I use `struct` to parse the
bytes into specific data. For example, if I know at `actor_address+0xAC0` there is a TArray, and I know TArrays are 
always 16 bytes (8 for the address of the array, 4 for the (int) current length of the array, and 4 for the (int) max 
length of the array), I can read 16 bytes at that address, then unpack that data into a list using a format of `<Qii`.
This will return me a list which looks like: `[memory_address(unsigned long long), current_length(int), 
max_length(int)]`. I can then pull the appropriate data out of that list as necessary

This is an alternative to reading the unsigned long long, then reading the first int, then reading the second int. 
While much more efficient than that alternative, this *may* not be as efficient as recreating the objects in their 
entirety.

Note: [See other `Structs` format information here](https://docs.python.org/3/library/struct.html#format-characters)

### Providing updates to this code base
If you are interested in helping maintain this code base, first off, thank you! My only asks are as follows:
1. Document your additions/changes in accordance with what exists
2. Utilize Pylint and the provided pylintrc file to ensure your code is 10/10 compliant prior to submission of a PR
3. Keep the framework a framework, do not add new features outside those listed in the "TODO" section
4. Create "Issues" if something strikes you as incorrect or needing improvement. Also consider looking at issues for
opportunities to contribute

### Other Offerings
https://github.com/DougTheDruid/SoT-Python-Offset-Finder - An attempt for me to keep an up-to-date SDK avaliable to the community, and a python file to automatically generate an offsets file based on your configuration
https://github.com/DougTheDruid/SoT-Actor-Names - A manually-created list that maps actors raw names to more common names

### TODO
- Automatically update the pyglet window location every X seconds to match SoT window location
- Handle weird issue where pyglet doesn't match the actual SoTWindow. Potential fix in `main.py`:
   ```python
    window = pyglet.window.Window(SOT_WINDOW_W-20, SOT_WINDOW_H-10,
                                  vsync=False, style='overlay',
                                  caption="DougTheDruid's ESP Framework")
    # window.set_caption('A different caption')
    hwnd = window._hwnd  # pylint: disable=protected-access

    # Move our window to the same location that our SoT Window is at
    window.set_location(SOT_WINDOW[0]+8, SOT_WINDOW[1])
   ```
- Update to calculate actual FOV correctly:
  Suspect its an issue with the "world to screen" method. changing fov calculation to 
   ```
   fov = player.get("fov")
   if fov == 20:
       fov = 19
   else:
       fov *= 1.03
   ```
   This fixes the issue with left/right for me. Can also modify `screen_center_y` to be = (SOT_WINDOW_H+30) / 2, 
   which might help with height issues if you have a title/task bar. If you also have issues with tracking, 
   but this doesn't fix it right away, I would recommend starting with this and modifying slightly. 

### Shoutouts!
I know without a doubt this framework wouldnt be nearly as polished as it is without the help of
a ton of people in the community. Sincerely thank you to everyone who has reached out and helped in any capacity!
Special thanks to: 

- [Gummy](https://www.unknowncheats.me/forum/members/726677.html) - Previously provided an opensource C++ version of a SoT Hack. Wouldnt have been possible without him!
- [miniman06](https://www.unknowncheats.me/forum/members/2903443.html) - Pattern recognition for automatic offset generation

