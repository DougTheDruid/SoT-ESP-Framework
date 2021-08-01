# Doug's Python SoT ESP Framework
Hello all! This is a framework to develop an SoT ESP Hack, all utilizing Python 3.7.9. This is a trimmed down version 
of a personal creation I utilize actively. This is a great foundation for someone who is looking to get started in 
ESP hacks for Sea of Thieves, and should be loaded with comments to help you grasp the "how" and "why" of basic 
memory editing and data display with Python. While this is intended for use within Sea of Thieves specifically, there is a lot
of resources utilized which could be useful in memory reading/editing for almost any game/program :D

This hack has the following implemented: 
- Get the location of ships in render distance and display them on screen
- Display a list of all players on the server

This is intentionally left as a framework and not a full-featured hack for a few reasons:
1. I already did the hard work of converting C functions to Python for you
2. I don't believe a fully-functioning hand-out would help progress the skill level of programmers
3. Much of the code is very well documented to help you understand the "how" of the hacks inner workings; as a 
   result many resources on hacking forums will give you guidelines for implementing new functionality; I did it myself, 
   you can to
4. I have undergone 3 or 4 major interations of this same code. **I am still learning** and re-writing functionality all 
   the time; a smaller code base is much more simple to maintain
   
I do ask that if you decided to take this into your own personal development, encourage others to think for themselves a
bit as well and try to maintain a "documenation-focesed" mindset as I have. I request that you do not use this 
framework for any commercial purposes (selling "your" version which is based on this framework) without contacting me and
recieving my approval prior.

### What version(s) of the game does this work with?
This hack will work with both versions of the game (Microsoft & Steam), and by default is configured to work for the 
Microsoft version. If you are using the Steam version, you will need to change the appropriate variable at the top
of SoTHack.py

### Why Python?!
Python is at its root a more user-friendly (IMO) version of C. Hypothetically, we can perform any C action using python,
but make it more readible and beginner-friendly. I am also much more comfortable developing in Python and saw this as
an opportunity to challenge myself.

### Prerequisites
In theory, all you need to get started in using this hack is Python 3.7.9, and to install the requirement found in the 
requirements.txt. The base framework relies on a 4k main monitor. You MAY need to make some minor changes in
the code to accomidate your display configuration (helpers.py, top of file). I personally run all of my Python from PyCharm, and 
start/stop the code execution through the built-in Run and Stop functionality. You may choose to implement proper 
"closing" functionality using pyglet. 

***As a test of faith, to get this code fully-functional you must modify one line of code and remove another entirely.
This is a VERY small countermeasure to ensure this framework is actually used as intended.***

### How to execute
At the time of writting, the script is built for a version of SoT with ~5 weeks left in Season 2 and given you have the
necessary pre-requisites, should execute with no major issues. Simply run `main.py` once you are in a server.

### How to update for new SoT Versions
If there has been a game version update:
   1. Load into a game server
   2. Open Cheat Engine 
   3. Open the `SoTGame.exe` process in Cheat Engine
   4. Change your "value type" to an "Array of byte"
   5. One-by-one enter the patterns found at the top of `sot_hack.py` (uWorld, gName, gObject) 
   6. Hit scan. Upon scanning, you should get one or two results, he top result is the one we want
   7. Extend the "Address" column to see all the data. Anything after "SoTGame.exe+" is our base offset
   8. Update the relevant BASE offsets in `sot_hack.py` at the top

If after performing those updates the hack is still not working, you may also need to update offsets found in the 
`offsets.json` file. If so, update the offsets according to the latest SDK ([this repo](https://github.com/pubgsdk/SoT-SDK) has been my go-to, with a custom 
script to read data out of the files automatically).

Running the script in Debug mode (set `debug`=`True` in `main.py` and utilize PyCharms Debug feature), may help you 
identify what offsets are *not* working correctly and need updating.

Note: There are some offsets hardcoded into the program, it is possible those hardcoded offsets CAN change and cause
your issues.

### cAn i GeT bAnNeD?!
TL;DR: Yes. You _can_ get banned, such is the risk of cheating.

Longer version: As is, this code purely utilizes a read-only state for the computers memory. With hundreds of hours utilizing these same read-only permissions, I have never been
banned, nor concerned for being banned. Does that guarentee you won't be? No. Does that guarentee you won't change something (like trying to write memory) that will cause you to 
get banned? No. If you arent sure what something does, or why something is done a certain way, do some research on the potential impact of changing it before actually changing it. 

### Can you help me implement X feature?
No. I learned utilizing already posted questions/comments easily found online, you can as well. This framework is meant for people who want to put in the work and learn something, 
not recieve a hand-out. You also may be able to see the FAQ.md for some useful information.
For community support, please contact me on Discord: DougTheDruid#2784

### How it works
When running `main.py`, an `SoTMemoryReader` object is created (found in `sot_hack.py`). That object creates a 
`ReadMemory` object (found in `memory_helper.py`) which is used to perform our requisite memory calls. We also create
a Pyglet window to display our data, and give Pyglet a set of instructions to run certain
update methods every so often (or every frame).

The `SoTMemoryReader` object gets data about the game world, but has a main game loop function called `read_actors`.
This method is responsible for determining how many actors there are, and reading data about all of those actors. For 
Actors we are interested in knowing more about, we create a relevant class-object to track their information. We also
use that object to build display information for Pyglet to utilize. 

Largely speaking, if you want to see the flow of the code, start at `main.py` and work your way down into the objects
and other files.

*This is an early build using Pyglet and probably isn't super optimized.*

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
2. Utilize Pylint and the provided pylintrc file to ensure your code is 10/10 compliant prior to submittion of a PR
3. Keep the framework a framework, do not add new features outside of those listed in the "TODO" section
4. Create "Issues" if something strikes you as incorrect or needing improvement. Also consider looking at issues for
opportunities to contribute
   
### TODO
- Implement an "auto-scanning" function for finding the base (uWorld, gName, gObject) offsets
- (Possibly) Recreating objects in their entirety in accordance with the SDK and compare to current speed
