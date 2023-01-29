# RisingWater

This is a program which simulates the flow of water and the erosion of rock with 2D-blocks. It was created with the Python GUI Tkinter.

Different Blocks with different properties are available:

- Water: Moves downwards and forms waterbodies. A waterbody tends to have a balanced surface.
- Air: Gets replaced by each other block moving at its position
- Rock: A block which stays where it is, unless it gets tranformed to sand
- Sand: Emerges from a Rock which is in contact with water for a longer time
- Water entry: Water blocks are created at this position
- Water exit: Water and sand gets removed at this position
