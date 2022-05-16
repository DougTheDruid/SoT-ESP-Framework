# Doug's Python SoT ESP Framework
Hello all! This is a framework to develop an SoT ESP Hack, all utilizing Python. This is a trimmed down version 
of a personal creation I utilize actively. This project is a great foundation for someone who is looking to get started in 
ESP hacks for SoT, other UE4 games, or games in general! The code is loaded with comments to help you grasp the "how" and "why" of basic 
memory editing and data display with Python. While as written this is intended for use within SoT specifically, there is a lot
of code which could be useful in memory reading/editing for almost any game/program.

## Getting Started
**This framework is strictly that, a framework. It is meant for _you_ to build _your own_ ESP hack upon the foundation I am providing. You NEED
to have basic Python programming experience in order to get started.**

### Installation Prerequisites & First Execution
In theory, all you need to get started in using this hack is Python 3.7.9 (have also verified in 3.9.6), and to install 
the requirements found in the `requirements.txt` file. With the requirements installed, ensure your game is in windowed mode,
enter a server, and run `main.py`. An overlay should appear over your game window with the count of the players on the server
to the top-right. The bottom-right should have a watermark for the framework and the bottom-left an FPS counter for the hack.
You MAY need to make some minor changes in the code to accommodate your specific display configuration 
(helpers.py, top of file). 

Debugging and error information will be available in the `DougsESP.log` file upon running the `main.py` file.

### First Steps
To ensure this framework is utilized appropriately, there are three intentional bugs you must fix in the code before it becomes
fully functional. At a high level, these three bugs are:
1) One line must be modified
2) One line must be removed entirely
3) One line must be uncommented

But how do you find these bugs? How do I know if I fixed the right thing? What if I need help?

### Finding the Bugs
In order to find the three bugs mentioned, you will need to go through **_all of the code_** and begin to understand what the methods,
files, variables, etc. all do in the context of the framework. Luckily there are a _lot_ of comments you can reference that
will help you grasp what is happening. But where do you start?

Since we are running our script from `main.py`, I generally advise that as a good place to start when understanding the framework.

When running `main.py`, an `SoTMemoryReader` object is created (found in `sot_hack.py`). `SoTMemoryReader` creates a
`ReadMemory` object (found in `memory_helper.py`) which is used to perform our requisite memory calls. We also create
a Pyglet window (our GUI) to display our data, and give Pyglet a set of instructions to run certain
update methods every so often (or every frame).

The `SoTMemoryReader` object gets data about the game world, but has a main game loop function called `read_actors`.
This method is responsible for determining how many actors there are, and reading data about all of those actors. For 
actors we are interested in knowing more about, we create a relevant class-object to track their information (e.g. `Ship` object). We also
use that object to build display information for Pyglet to utilize. 

There is a bit of depth to some logic, but generally any good IDE should allow you to navigate around the different
custom objects and methods fairly easily. Almost every line has been excruciatingly commented for _your_ benefit. Be sure to read them
and reach out if you have any issues.

The framework features outlined below should all be working once you correct the three bugs. They may also provide a bit
of guidance as to where to look to find those bugs.

### Framework Features
This hack has the following implemented:
- Get the location of ships in render distance and display them on screen
- Display a count of the players on the server
- Display a list of all players on the server, and update the list correctly

## Your First Additions
Once you have accomplished getting the framework working as intended, you may find yourself asking, what do I do next?
Generally I recommend adding one of the following for your "first addition" to the framework. These should serve as a good
starting point before attempting any complex additions such as cannon-prediction, x-marks the spot, etc.:
- Loot ESP
- Player ESP
- AI ESP
- World item additions (Rowboats, Seagulls, etc.)

### Finding Interesting Actors
Once you have decided what you want to add generally (loot, players, etc.), you then need to work on finding the relevant in-game
actor name(s) that match the type of entity you want to track. For example, in `mapping.py` we can see that a near-by Sloop
has an actor name of `BP_SmallShipNetProxy_C`. But how do you find those actor names?

There are a lot of different ways you can find potentially interesting actors to implement in your person version(s), but here
are a couple of options I've used:
1) Print out all the actor names
2) Create a "Debug" Module (more below) that tries to generate 3d coordinates and screen coordinates for every actor in render distance.
You may have to exclude some known-non-helpful actors to help it remain speedy
3) Review the common mappings I provide here: https://github.com/DougTheDruid/SoT-Actor-Names/blob/main/actors.json

You will then need to add the actor you are interested in to your `mapping.py` file (note: Some decide to split the mapping file into multiple lists/dictionaries),
create an appropriate "Module" to handle that actor type, and finally add logic to the `read_actors` loop to create that module.

Speaking of modules...

### Modules
In my personal version of this framework, I create a separate "Module" to plug into
my hack similarly to how a `Ship` object is created in the framework. This allows me to have all unique logic to parse
data for a given entity type in one location. I recommend using this strategy as it helps keep your `sot_hack.py` file clean.

I will start by copying an existing module and renaming it appropriately, this will ensure I have a "working" foundation to start from.
Then it is a matter of making the appropriate changes to the copied module to "fit" the new data-type you are looking to track.
This is going to vary pretty wildly, but here are some high-level considerations for working with modules:
- By default, every 5 seconds new entities around the player are created with their respective module, but every frame, the `update` method
for each entity is called, allow it to track new positions/data within that 5sec delay. This drastically helps performance and I recommend
trying to maintain this
- Almost all entities coordinates are located at the same offset, but some entities will have additional coordinate-type information
you can leverage in a similar memory location
- Our `update` methods can also help "switching" between near and far entities, such as with ships. "Hiding" one entity once
conditions are met, or showing another. `visbile` is a great control over what is showing/not showing on the screen and can be tricky to grasp

Modules are very powerful, but only as powerful as the custom logic you build behind them unique to your specific actor-type data.
In order to find that interesting data, we need to start digging into the SDK...

### Finding Interesting Actor Data
Each actor in SoT has tons of data in memory backing it. Position, names, linked entities, etc. all make up just some
of what memory data may be available for each actor. But how do you know what memory data to use? or what's even available?

Once you have identified an actor name that you have interest in, we can begin to look through what is known as the SDK (Software Development Kit)
for the game. This SDK can change during a patch, and luckily, I provide three versions here: https://github.com/DougTheDruid/SoT-Python-Offset-Finder/tree/main/SDKs
There is more information in the `readme.md` file for this repo, but generally speaking, we can [search the SDK](https://github.com/DougTheDruid/SoT-Python-Offset-Finder/blob/main/README.md#sdk-utilization)
and determine what interesting attributes an actor has that we can read from. 

Note: It's also important to note that we can use the memory from _parent_ classes as well when reading for an actor.
For example if we have an entity of `IslandService`, `IslandService` is a child of `Actor`, so we can leverage the memory data
as if our object was an `Actor`-type as well.


### Programming Structs
Another resource-saving technique utilized in the framework is `structs`. Instead of rebuilding structures similarly 
to how you would in C or C++, I utilize something fairly frequently in my code that may not be very clear called 
`struct`. This is a Python-native import which allows us to more easily convert hex data to a list of information.

I read a number of bytes at a memory location given what I want to grab, then I use `struct` to parse the
bytes into specific data. For example, if I know at `actor_address+0xAC0` there is a TArray, and I know TArrays are 
always a total of 16 bytes (8 for the address of the array, 4 for the (int) current length of the array, and 4 for the (int) max 
length of the array), I can read 16 bytes at that address, then unpack that data into a list using a format of `<Qii`.
This will return me a list which looks like: `[memory_address(unsigned long long), current_length(int), 
max_length(int)]`. I can then pull the appropriate data out of that list as necessary

This is an alternative to reading the unsigned long long, then reading the first int, then reading the second int. 
While much more efficient than that alternative, this *may* not be as efficient as recreating the objects in their 
entirety and can be rather confusing

Note: [See other `Structs` format information here](https://docs.python.org/3/library/struct.html#format-characters)

## Final Considerations
I do ask that if you decided to take this into your own personal development, encourage others to think for themselves a
bit as well and try to maintain a "documentation-focused" mindset as I have. I request that you do not use this 
framework for any commercial purposes (selling "your" version which is based on this framework) without contacting me and
receiving my approval prior.

If you need help, please see the [Frequently Asked Questions](https://github.com/DougTheDruid/SoT-ESP-Framework/blob/main/FAQ.md)
and if none of those apply or help, reach out to me on Discord: DougTheDruid#2784

### Providing updates to this code base
If you are interested in helping maintain this code base, first off, thank you! My only asks are as follows:
1. Document your additions/changes in accordance with what exists
2. Utilize Pylint and the provided pylintrc file to ensure your code is 10/10 compliant prior to submission of a PR
3. Keep the framework a framework, do not add new features outside those listed in the "TODO" section
4. Create "Issues" if something strikes you as incorrect or needing improvement. Also consider looking at issues for
opportunities to contribute

### Other Offerings
I maintain a number of SoT/Hacking related repos you may find beneficial. Each should have a helpful `readme.md` file to get started.

https://github.com/DougTheDruid/SoT-Python-Offset-Finder - An attempt for me to keep an up-to-date SDK available to the community, and a 
python file to automatically generate an offsets file based on your configuration, resulting in an `offsets.json` file the framework uses

https://github.com/DougTheDruid/SoT-Actor-Names - A manually-created list that maps actors raw names to more common names

### TODO
- Automatically update the pyglet window location every X seconds to match SoT window location
- Handle weird issue where pyglet doesn't match the actual SoTWindow. This is caused by the fading around Windows.
Potential fix in `main.py`:
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
  Suspect its an issue with the "world to screen" method. Changing fov calculation to 
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

### Shout-outs!
I know without a doubt this framework wouldn't be nearly as polished as it is without the help of
a ton of people in the community. Sincerely thank you to everyone who has reached out and helped in any capacity!
Special thanks to: 

- [Gummy](https://www.unknowncheats.me/forum/members/726677.html) - Previously provided an opensource C++ version of a SoT Hack. Wouldn't have been possible without him!
- [miniman06](https://www.unknowncheats.me/forum/members/2903443.html) - Pattern recognition for automatic offset generation
- [mogistink](https://www.unknowncheats.me/forum/members/3434160.html) - Supreme helper of the community and always providing valuable feedback on changes
