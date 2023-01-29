## Userinterface, Design

from pickle import FALSE

CANVAS_START=20

WINDOW_WIDTH=1000

WINDOW_HEIGHT=880

DEFAULT_SPEED = 8

BLOCK_SIZE = 30

BLOCK_COLOR = {"air": "white", "water": "blue", "earth": "brown", "sand": "yellow",
                 "water_entry": "black", "water_exit": "gray"}

# BLOCK_TYPE = {"air": AirBlock(), "water": WaterBlock(), "earth": EarthBlock(), "sand": SandBlock(),
#                 "water_entry": WaterEntryBlock(), "water_exit": WaterExitBlock()}

SPEED_STEPS = 11

EXTEND_X = 30

EXTEND_Y = 25

SAVE_FOLDER = '/home/christoph/Own_projects/RisingWater/worlds' 


## Game mechanics ##

AIR_BLOCK_BELOW_CRITICAL_DISTANCE = 2
AIR_BLOCK_SIDE_CRITICAL_DISTANCE = 4

EROSION = False