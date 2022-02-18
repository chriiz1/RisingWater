from tkinter import * 
from tkinter.constants import TRUE
from turtle import speed
import constants
from world import *

class UI:
    def __init__(self, world: World):
        # root
        root = Tk()
        root.title("RisingWater")
        root.geometry(f'{constants.WINDOW_WIDTH}x{constants.WINDOW_HEIGHT}')
        
        # canvas
        canvas = Canvas(root)
        canvas.configure(bg="White")
        canvas.pack(fill="both", expand=True)

        # speed
        speed_widget = Scale(root, from_=1, to=constants.SPEED_STEPS, length = 200, orient=HORIZONTAL)
        speed_widget.set(constants.DEFAULT_SPEED)

        # class attributes
        self.root = root
        self.canvas = canvas
        self.speed = speed_widget #??
        self.world = World()
        self.running = False
        self.selected_block_type = "earth"
        self.start_stop_text = tk.StringVar(value="Run")

        # start/stop
        btn_start_stop = Button(root, textvariable=self.start_stop_text, command = self.toogle_start_stop, width=10)
        btn_start_stop.pack(side = LEFT, padx=20)
        btn_clear_all = Button(root, text= "Clear world", command = self.clear_world, width=9,activebackground='#ff4444')
        btn_clear_all.pack(side = LEFT, padx=20)
        speed_widget.pack(side = LEFT, padx=(20,50))
        btn_save = Button(root, text ="Save default", command = world.save_default)
        btn_save.pack(side = LEFT)
        btn_load = Button(root, text ="Load default", command = world.load_default)
        btn_load.pack(side = LEFT, padx=(10,30))
        btn_save = Button(root, text ="Save as", command = world.save_as)
        btn_save.pack(side = LEFT)
        btn_load = Button(root, text ="Load ", command = world.load)
        btn_load.pack(side = LEFT)

        # context
        m = Menu(self.root, tearoff = 0)
        m.add_command(label ="air", command = lambda arg1 = "air": self.set_selected_block_type(arg1))
        m.add_command(label ="water", command = lambda arg1 = "water": self.set_selected_block_type(arg1))
        m.add_command(label ="earth", command = lambda arg1 = "earth": self.set_selected_block_type(arg1))
        m.add_command(label ="water_entry", command = lambda arg1 = "water_entry": self.set_selected_block_type(arg1))
        m.add_command(label ="water_exit", command = lambda arg1 = "water_exit": self.set_selected_block_type(arg1))
        canvas.bind("<Button-3>", lambda event, arg1 = m: self.show_context_menu(event, arg1))

        # drawing
        canvas.bind('<ButtonPress-1>', lambda event, arg1 = world: self.on_down(event, arg1))
        canvas.bind('<ButtonRelease-1>', lambda _, arg1 = world: self.on_up(arg1))
        canvas.bind('<Motion>', lambda event, arg1 = world: self.mouse_move(event, arg1))
        self. world = world
        world.ui = self

    def main(self):
        '''
        The core of the programm. This loop rans forever...
        '''    
        if self.running:
            self.world.organise_water_blocks()
            self.world.move_blocks()
            self.world.draw()
            self.root.update()
            self.draw_on_tick()
        self.root.after(self.get_speed(), self.main)

    def toogle_start_stop(self):
        if self.running:
            self.running = False
            self.start_stop_text.set("Run")
        else:
            self.running = True
            self.start_stop_text.set("Stop")
    
    def get_speed(self):
        control_val = self.speed.get()
        speed = (constants.SPEED_STEPS - control_val + 1) ** 3
        return speed

    def stop(self):
        self.running = False

    def set_selected_block_type(self, type):
        self.selected_block_type = type

    def clear_world(self):
        for _,block in self.world.blocks.items():
            block.type = 'air'
            block.subtype = 'air'
        self.world.draw()
        self.root.update()
        if self.running:
            self.toogle_start_stop()

    def get_block_references(self, world: World, x_pos: int, y_pos: int):
        '''
        gets the position and the associated polygon of a block
        '''

        # checks if the mouse is inside the canvas
        if (x_pos >= constants.CANVAS_START + constants.BLOCK_SIZE * world.extend[X] or 
            y_pos >= constants.CANVAS_START + constants.BLOCK_SIZE * world.extend[Y] or 
            x_pos < constants.CANVAS_START or y_pos < constants.CANVAS_START):
            return None, None

        index_x = int((x_pos - constants.CANVAS_START) / constants.BLOCK_SIZE)
        index_y = int((y_pos - constants.CANVAS_START) / constants.BLOCK_SIZE)
        block_pos = (index_x, index_y)

        # pol_ref = the polygon in the canvas to which the block is associated
        pol_ref = world.blocks[block_pos].pol_ref

        return pol_ref, block_pos

    def change_block(self, mouse_pos, world: World):
        '''
        change a block to the selected block type
        '''
        pol_ref, block_pos = self.get_block_references(world, mouse_pos[X], mouse_pos[Y])

        if pol_ref is not None:
            color = constants.BLOCK_COLOR[self.selected_block_type]
            world.canvas.itemconfig(pol_ref, fill = color)

            if self.selected_block_type == 'water_entry':
                world.blocks[block_pos].type = 'water'
                world.blocks[block_pos].subtype = self.selected_block_type
            elif self.selected_block_type == 'water_exit':
                world.blocks[block_pos].type = 'air'
                world.blocks[block_pos].subtype = self.selected_block_type
            else:
                world.blocks[block_pos].type = self.selected_block_type
                world.blocks[block_pos].subtype = self.selected_block_type
                
    def on_down(self, event, world):
        world.drawing = True
        self.change_block((event.x, event.y), world)

    def draw_on_tick(self):
        if self.world.drawing:
            x = self.root.winfo_pointerx()
            y = self.root.winfo_pointery()
            abs_coord_x = self.root.winfo_pointerx() - self.root.winfo_rootx()
            abs_coord_y = self.root.winfo_pointery() - self.root.winfo_rooty()

            self.change_block((abs_coord_x,abs_coord_y), self.world)
        pass

    def mouse_move(self, event, world):
        if world.drawing:
            self.change_block((event.x, event.y), world)

    def on_up(self, world):
        world.drawing = False

    def show_context_menu(self, event, m):
        try:
            m.tk_popup(event.x_root, event.y_root)
        finally:
            m.grab_release()