### When I run the hack, nothing shows up
If you JUST run the hack as-is without changing any code, you should **only** see a player count at the top right
of the window. There are more features mentioned in the readme.md, but there is work required
to get those functions operational; these are also mentioned in the readme.md (Prerequisites section)

Check the following:
1. By default, it works for the Microsoft version of the game, there is a variable to toggle if you are using Steam. 
   Does this apply to you? Did you change the toggle?
2. Validate you have a pyglet window that is opening and there are no errors DougsESP.log
3. Have you corrected the tests of faith mentioned in the readme.md (Prerequisites section)?
4. Are you running in windowed mode?

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

### What do I do first?
First, you should get the hack to a state where all the features mentioned in the readme are working as expected.
After that I recommend reading through: https://github.com/DougTheDruid/SoT-Python-Offset-Finder#how-to-search-the-sdk to 
gain some additional understanding on how to work with the SDK. You may then take a look through the below list, pick one small
component to implement, and give it your best shot. Ask for help on Discord.

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
