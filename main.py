import constants
import world
from user_interface import *

if __name__ == "__main__":
    w = world.World([constants.EXTEND_X, constants.EXTEND_Y])
    ui = UI(w)
    w.root = ui.root
    w.canvas = ui.canvas
    ui.world.generate_empty_world(ui.canvas)
    ui.root.update()
    ui.main()
    ui.root.mainloop()

    # https://stackoverflow.com/questions/27050492/how-do-you-create-a-tkinter-gui-stop-button-to-break-an-infinite-loop
    # https://gamedev.stackexchange.com/questions/58734/simulating-pressure-in-a-grid-based-liquid-simulation
    # http://www.jgallant.com/2d-liquid-simulator-with-cellular-automaton-in-unity/