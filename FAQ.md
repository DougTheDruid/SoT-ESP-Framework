### When I run the hack, nothing shows up
If you JUST run the hack as-is without changing any code, you should **only** see a player count at the top right
of the window. You MAY need to change where that is being displayed on the screen dependent on your monitor size. To
change that position in the main.py file. There are more features mentioned in the readme.md, but there is work required
to get there also mentioned in the readme.md (Prerequisites section)

Check the following:
1. By default, it works for the Microsoft version of the game, there is a variable to toggle if you are using Steam. 
   Does this apply to you?
2. Validate you have a pygame window that is opening and there are no errors in the python window
3. Have you made sure all of your window sizes have been updated according to the readme?
4. Have you corrected the tests of faith mentioned in the readme.md (Prerequisites section)?
5. Are you running in windowed mode?

### What do I do first?
First, you should get the hack to a state where all of the features mentioned in the readme are working as expected.
Once you are familiar with the hack and how the code operates, I would take a look through the below list, pick one small
component to implement, and give it your best shot. Ask for help on Discord

### Do you have a list of things I can do with this hack?
Things I (and others) have implemented utilizing this framework:
- Ship ESP (Distance, Sunk %, and Type)
- Player ESP (Distance, HP, Name, and Currently Wielding)
- Skeleton ESP (Distance, Max HP)
- Loot ESP (Distance, Color-coding by "value", and grouping by proximity if I desire)
- X-Marks the spot ESP for normal treasure maps
- World object ESP (Rowboats, Events, Seagulls/Shipwrecks, Quest Areas, etc)
- Player data for the server (count, names, who joined when, etc)
- Crew data for the players on the server
- Current camera compass heading & bearing 
- Cannon trajectory calculation
