from tkinter import *
import tkinter
from tkinter import messagebox 
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
        canvas = Canvas(root, width=constants.WINDOW_WIDTH-50, height=constants.WINDOW_HEIGHT-80)
        canvas.configure(bg="White")
        canvas.grid(column=0,row=0,columnspan=6)

        # speed
        speed_widget = Scale(root, from_=1, to=constants.SPEED_STEPS, length = 200, orient=HORIZONTAL)
        speed_widget.set(constants.DEFAULT_SPEED)

        # class attributes
        self.root = root
        self.canvas = canvas
        self.speed = speed_widget 
        self.world = World()
        self.running = False
        self.selected_block_type = "earth"
        self.start_stop_text = tk.StringVar(value="Run")
        self.erosion = tkinter.IntVar(value=1)
        self.start_stop_btn = None

        btn_start_stop = Button(root, textvariable = self.start_stop_text,
                command = self.toogle_start_stop, width=10, font="bold",bg="green",activebackground="lightgreen")
        btn_start_stop.grid(row=1, column=0)
        self.start_stop_btn = btn_start_stop    
        btn_clear_all = Button(root, text= "Clear world", command = self.clear_world, width=9, activebackground='#ff4444')
        btn_clear_all.grid(row=2,column=0)
        speed_label = Label(root,text="Which speed?")
        speed_label.grid(row=1,column=1,sticky=E)
        speed_widget.grid(row=1,column=2)
        erosion_label = Label(root,text="Erosion?")
        erosion_label.grid(row=2,column=1,sticky=E)
        erosion_cbx = Checkbutton(root, variable=self.erosion)
        erosion_cbx.grid(row=2,column=2,sticky=W,padx=20)
        btn_save = Button(root, text ="Save default", command = world.save_default)
        btn_save.grid(row=1,column=3)
        btn_load = Button(root, text ="Load default", command = world.load_default)
        btn_load.grid(row=2,column=3)
        btn_save = Button(root, text ="Save as", command = world.save_as)
        btn_save.grid(row=1,column=4)
        btn_load = Button(root, text ="Load ", command = world.load)
        btn_load.grid(row=2,column=4)
        btn_help = Button(root, text ="Please help \n me :( ", command = self.show_help)
        btn_help.grid(row=1,column=5, rowspan=2,sticky=E)

        # context
        m = Menu(self.root, tearoff = 0)
        m.add_command(label ="air", command = lambda arg1 = "air": self.set_selected_block_type(arg1))
        m.add_command(label ="water", command = lambda arg1 = "water": self.set_selected_block_type(arg1))
        m.add_command(label ="earth", command = lambda arg1 = "earth": self.set_selected_block_type(arg1))
        m.add_command(label ="sand", command = lambda arg1 = "sand": self.set_selected_block_type(arg1))
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
            self.world.analyse_blocks()
            self.world.move_blocks()
            if self.erosion.get() == 1:
                self.world.analyse_earth_blocks()
                self.world.analyse_sand_blocks()
            self.world.draw()
            self.world.end_tick()
            self.root.update()
            self.draw_on_tick()
        self.root.after(self.get_speed(), self.main)

    def toogle_start_stop(self):
        if self.running:
            self.running = False
            self.start_stop_text.set("Run")
            self.start_stop_btn.configure(bg="green",activebackground="lightgreen")
        else:
            self.running = True
            self.start_stop_text.set("Stop")
            self.start_stop_btn.configure(bg="red",activebackground="tomato")

    def show_help(self):
        messagebox.showinfo("Some hints ;) ","1. Right Click for changing Block Type\n2. You can disable the Erosion!\n3. Use Load-/Save Default for quicker loading and saving")
        

    def get_speed(self):
        control_val = self.speed.get()
        speed = (constants.SPEED_STEPS - control_val + 1) ** 3
        return speed

    def stop(self):
        self.running = False

    def set_selected_block_type(self, type):
        self.selected_block_type = type

    def clear_world(self):
        previously_running = self.running
        if self.running:
            self.toogle_start_stop()
        result = messagebox.askquestion("Clear the world", "Are you sure?", icon='warning')
        if result != 'yes':
            if previously_running:
                self.toogle_start_stop()
            return
        new_blocks = {}
        for pos,block in self.world.blocks.items():
            new_block = Block.get_block("air", block.get_pos(), block.pol_ref,block.world)
            new_blocks[(pos[X], pos[Y])] = new_block
        self.world.blocks = new_blocks
        self.world.draw()
        self.root.update()

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
            new_block = Block.get_block(self.selected_block_type, pos=block_pos, pol_ref=pol_ref,world_ref=world)
            world.blocks[block_pos] = new_block
                
    def on_down(self, event, world):
        world.drawing = True
        self.change_block((event.x, event.y), world)

    def draw_on_tick(self):
        if self.world.drawing:
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