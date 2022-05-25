## Troubleshooting
### When I run the hack, nothing shows up
If you JUST run the hack as-is without changing any code, you should **only** see a player count at the top right
of the window. There are more features mentioned in the readme.md, but there is work required
to get those functions operational; these are also mentioned in the readme.md (Prerequisites section)

Check the following:
1. Is your framework up-to-date?
2. Is SoT currently running and are you on server?
3. Are you running your SoT Game in windowed mode?
4. Validate you have a pyglet window that is opening and there are no errors DougsESP.log
5. If the program is running, have you corrected the tests of faith mentioned in the readme.md (Prerequisites section)?

### Rendered items in the hack (text/circles) are fuzzy and larger than they should be
If you have windows scaling on (for a large/high DPI monitor), you may need to make a small change to python to avoid
your pyglet window also scaling:
1. Navigate to your python folder (Mine is `C:\Python37` for example)
2. Right-click your `python.exe` application and select "Properties"
3. Select the "Compatibility" tab at the top
4. Select "Change high DPI Setting"
5. Check the box labelled "Override high DPI scaling behavior. Scaling performed by:"
6. Select "Application" in the dropdown 
7. Select "OK"
8. Select "Apply" and then "OK" 

### When I run the hack, all entities 3D markers appear at (0,0,0) coordinates, not on the actual entity
More than likely this is caused by a recent update to the game. There is no "expected" SDK value that represents an
actors coordinates as far as I have found. As such, we rely on a manually-determined field in our `offsets.json` file
to tell us where these coordinates live for each actor. Please review the commends in the 
`SoT-Python-Offset-Finder/offset_finder.py` file. You will more than likely need to update this offset to reflect where
the coordinates are actually stored now. Please contact me on discord if you encounter this issue.


To fix yourself: Open Cheat Engine (or your favorite memory browser) and around the old offset, try and find a 
new Vector (3 floats) that look like they may be coords (X, Y, and Z in that order). I think its -50,000 to 50,000 for
X & Y, Z=0=Sea level. Try the offset at the start of the X coord and see if it works.

### I think some offsets are wrong, how do I fix them?
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
`offsets.json` file. If so, update the offsets according to the latest SDK (various providers available on Unknown Cheats, or [try mine if its up to date](https://github.com/DougTheDruid/SoT-Python-Offset-Finder/tree/main/SDKs)). You may also use [my offset
finder](https://github.com/DougTheDruid/SoT-Python-Offset-Finder) to help pull the appropriate data from the SDK files

Running the script in Debug mode (set `debug`=`True` in `main.py` and utilize PyCharms Debug feature), may help you 
identify what offsets are *not* working correctly and need updating.

Note: There are some offsets hardcoded into the program, it is possible those hardcoded offsets CAN change and cause
your issues.

## General Questions
### How can I contact you?
Please, before contacting me ensure that you have read through the entire `readme.md` and `faq.md` files:
Discord: DougTheDruid#2784

### Why is this only a framework? Do you offer a full version? Or paid version?
1. I already did the hard work of converting C functions to Python for you
2. I don't believe a fully-functioning hand-out would help progress the skill level of programmers
3. Much of the code is very well documented to help you understand the "how" of the hacks inner workings; as a 
   result many resources on hacking forums will give you guidelines for implementing new functionality; I did it myself, 
   you can to
4. I have undergone 6 or 7 major iterations of this same code. **I am still learning** and re-writing functionality all 
   the time; a smaller code base is much more simple to maintain

**I have never and do not intend to make a full version publicly available, for sale or otherwise.**

### Can you help me implement X feature?
No. I learned to utilize already posted questions/comments easily found online, you can as well. This framework is meant for people who want to put in the work and learn something, 
not receive a hand-out.
For community support, please contact me on Discord: 

### cAn i GeT bAnNeD?!
TL;DR: Yes. You _can_ get banned, such is the risk of cheating.

Longer version: As is, this code purely utilizes a read-only state for the computer's memory. With hundreds of hours utilizing these same read-only permissions, I have never been
banned, nor concerned for being banned. Does that guarantee you won't be? No. Does that guarantee you won't change something (like trying to write memory) that will cause you to 
get banned? No. If you aren't sure what something does, or why something is done a certain way, do some research on the potential impact of changing it before actually changing it.

### Does this work with both Steam & Microsoft versions?
This hack will work with both versions of the game (Microsoft & Steam). It is confirmed to work on running Windows 10 and Windows 11.

### Why Python?!
Python is at its more user-friendly version of C. Hypothetically, we can perform any C action using python,
but make it more readable and beginner-friendly. I am also much more comfortable developing in Python and saw this as
an opportunity to challenge myself.

### Do you have a list of things I can do with this hack?
Things I (and others) have implemented utilizing this framework:
- Ship ESP (Distance, Sunk %, and Type)
- Player ESP (Distance, HP, Name, and Currently Wielding)
- Skeleton ESP (Distance, Max HP)
- Loot ESP (Distance, Color-coding by "value", and grouping by proximity if I desire)
- X-Marks the spot ESP for normal treasure maps
- World object ESP (Rowboats, Events, Seagulls/Shipwrecks, Quest Areas, etc.)
- Player data for the server (count, names, who joined when, etc.)
- Crew data for the players on the server
- Current camera compass heading & bearing 
- Cannon trajectory calculation
