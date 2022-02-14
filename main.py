from tkinter import * 
from tkinter.constants import TRUE
import constant
from classes import *

X = 0
Y = 1

def get_rectangle_ref(world, x_pos, y_pos):
    if (x_pos >= constant.CANVAS_START + constant.BLOCK_SIZE * world.extend[X] or 
        y_pos >= constant.CANVAS_START + constant.BLOCK_SIZE * world.extend[Y] or 
        x_pos < constant.CANVAS_START or y_pos < constant.CANVAS_START):
        return None, None
    index_x = int((x_pos - constant.CANVAS_START) / constant.BLOCK_SIZE)
    index_y = int((y_pos - constant.CANVAS_START) / constant.BLOCK_SIZE)
    block_ref = (index_x, index_y)
    pol_ref = world.blocks[block_ref].pol_ref
    return pol_ref, block_ref

def change_block(event, world):
    pol_ref, block_ref = get_rectangle_ref(world, event.x, event.y)
    if pol_ref is not None:
        color = constant.BLOCK_COLOR[world.selected_block_type]
        world.canvas.itemconfig(pol_ref, fill = color)

        if block_ref in world.water_exits:
            world.water_exits.remove(block_ref)
        if block_ref in world.water_entries:
            world.water_entries.remove(block_ref)
        if world.selected_block_type == 'water_entry' and block_ref not in world.water_entries:
            world.water_entries.append(block_ref)
            world.blocks[block_ref].type = 'water'
        elif world.selected_block_type == 'water_exit'and block_ref not in world.water_exits:
            world.water_exits.append(block_ref)
            world.blocks[block_ref].type = 'air'
        else:
            world.blocks[block_ref].type = world.selected_block_type

def on_down(event, world):
    world.drawing = True
    change_block(event, world)

def mouse_move(event, world):
    if world.drawing:
        change_block(event, world)

def on_up(world):
    world.drawing = False

def show_context_menu(event, m):
    try:
        m.tk_popup(event.x_root, event.y_root)
    finally:
        m.grab_release()

def setup_ui(world):
    # root
    root = Tk()
    root.title("RisingWater")
    root.geometry(f'{constant.WINDOW_WIDTH}x{constant.WINDOW_HEIGHT}')
    
    # canvas
    canvas = Canvas(root)
    canvas.configure(bg="White")
    canvas.pack(fill="both", expand=True)

    # speed
    speed_widget = Scale(root, from_=1, to=constant.SPEED_STEPS, length = 200, orient=HORIZONTAL)
    speed_widget.set(constant.DEFAULT_SPEED)
    ui = UI(root, canvas, speed_widget)

    # start/stop
    btn_start_stop = Button(root, textvariable=ui.start_stop_text, command = ui.toogle_start_stop, width=10)
    btn_start_stop.pack(side = LEFT, padx=20)
    btn_clear_all = Button(root, text= "Clear world", command = ui.clear_world, width=9,activebackground='#ff4444')
    btn_clear_all.pack(side = LEFT, padx=20)
    speed_widget.pack(side = LEFT, padx=(20,50))
    btn_save = Button(root, text ="Save default", command = world.save)
    btn_save.pack(side = LEFT)
    btn_load = Button(root, text ="Load default", command = world.load)
    btn_load.pack(side = LEFT, padx=(10,30))
    btn_save = Button(root, text ="Save as", command = world.save2)
    btn_save.pack(side = LEFT)
    btn_load = Button(root, text ="Load ", command = world.load2)
    btn_load.pack(side = LEFT)

    # context
    m = Menu(root, tearoff = 0)
    m.add_command(label ="air", command = lambda arg1 = "air": world.set_selected_block_type(arg1))
    m.add_command(label ="water", command = lambda arg1 = "water": world.set_selected_block_type(arg1))
    m.add_command(label ="earth", command = lambda arg1 = "earth": world.set_selected_block_type(arg1))
    m.add_command(label ="water_entry", command = lambda arg1 = "water_entry": world.set_selected_block_type(arg1))
    m.add_command(label ="water_exit", command = lambda arg1 = "water_exit": world.set_selected_block_type(arg1))
    canvas.bind("<Button-3>", lambda event, arg1 = m: show_context_menu(event, arg1))

    # drawing
    canvas.bind('<ButtonPress-1>', lambda event, arg1 = world: on_down(event, arg1))
    canvas.bind('<ButtonRelease-1>', lambda _, arg1 = world: on_up(arg1))
    canvas.bind('<Motion>', lambda event, arg1 = world: mouse_move(event, arg1))
    ui.world = world
    world.ui = ui
    return ui

if __name__ == "__main__":
    import random as rnd
    rnd.choice(range(0,19))
    world = World([constant.EXTEND_X, constant.EXTEND_Y])
    ui = setup_ui(world)
    world.root = ui.root
    world.canvas = ui.canvas
    ui.world.generate(ui.canvas)
    ui.root.update()
    ui.main()
    ui.root.mainloop()
    a = 3
    b = 4
    f'{a}+{b}'


    # https://stackoverflow.com/questions/27050492/how-do-you-create-a-tkinter-gui-stop-button-to-break-an-infinite-loop
    # https://gamedev.stackexchange.com/questions/58734/simulating-pressure-in-a-grid-based-liquid-simulation
    # http://www.jgallant.com/2d-liquid-simulator-with-cellular-automaton-in-unity/