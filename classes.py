import os
import constant
import json
import math
import numpy as np
import random as rnd
import tkinter as tk
from tkinter import filedialog
X = 0
Y = 1

class UI:
    def __init__(self, root, canvas, speed):
        self.root = root
        self.canvas = canvas
        self.speed = speed
        self.world = None
        self.running = False
        self.pointer = [0,0]
        self.start_stop_text = tk.StringVar(value="Run")

    def main(self):    
        if self.running:
            self.world.analyse()
            self.world.move_blocks()
            Waterbody.register = []
            self.world.update_blocks()
            self.root.update()
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
        speed = (constant.SPEED_STEPS - control_val + 1) ** 3
        return speed

    def stop(self):
        self.running = False
    
    def clear_world(self):
        for _,block in self.world.blocks.items():
            block.type = 'air'
        self.world.water_entries = []
        self.world.water_exits = []
        self.world.update_blocks()
        self.root.update()
        if self.running:
            self.toogle_start_stop()

class World:
    def __init__(self, extend, blocks = {}):
        self.extend = extend
        self.blocks = blocks
        self.drawing = False
        self.root = None
        self.canvas = None
        self.waterbodies = []
        self.watercolumns = {}
        self.selected_block_type = "earth"
        self.water_entries = []
        self.water_exits = []
        self.ui = None
    
    def set_selected_block_type(self, type):
        self.selected_block_type = type

    def generate(self, canvas):
        block_size = constant.BLOCK_SIZE
        for x in range (self.extend[X]):
            for y in range (self.extend[Y]):
                start_x = constant.CANVAS_START + (x * block_size)
                start_y = constant.CANVAS_START + (y * block_size)
                points = [start_x, start_y, start_x + block_size, start_y, start_x + block_size, start_y + block_size, start_x, start_y + block_size]
                ref = canvas.create_polygon(points, fill="white", outline="black")
                block = Block("air", x, y, ref, self)
                self.blocks[(x,y)] = block

    def prepare_save_file(self):
        output = {str(key): {'type': value.type} for key, value in self.blocks.items()}
        for key, value in output.items():
            if eval(key) in self.water_entries:
                value['extra'] = 'water_entry' 
        for key, value in output.items():
            if eval(key) in self.water_exits:
                value['extra'] = 'water_exit'
        return output

    def save(self):
        file = '/home/christoph/Own_projects/RisingWater/worlds/default.json'
        with open(file, 'w') as json_file:
            output = self.prepare_save_file()
            json.dump(output, json_file)
    
    def save2(self):
        initialdir='/home/christoph/Own_projects/RisingWater/worlds' 
        f = filedialog.asksaveasfile(mode='w', defaultextension=".txt", initialdir=initialdir)
        if f is None: # asksaveasfile return `None` if dialog closed with "cancel".
            return
        output = self.prepare_save_file()
        text2save = json.dumps(output)
        f.write(text2save)
        f.close() # `()` was missing.

    def load(self, filename = 'default.json'):
        file = os.path.join('/home/christoph/Own_projects/RisingWater/worlds', filename)
        with open(file, 'r') as json_file:
            input = json.load(json_file)
            self.water_entries = []
            self.water_exits = []
            for key, block in input.items():
                key = eval(key)
                self.blocks[key].type = block['type']
                color = constant.BLOCK_COLOR[block['type']]
                self.canvas.itemconfig(self.blocks[key].pol_ref, fill =color)
                if 'extra' in block:
                    if block['extra'] == 'water_entry':
                        self.water_entries.append(key)
                        self.canvas.itemconfig(self.blocks[key].pol_ref, fill =constant.BLOCK_COLOR['water_entry'])
                    if block['extra'] == 'water_exit':
                        self.water_exits.append(key)
                        self.canvas.itemconfig(self.blocks[key].pol_ref, fill =constant.BLOCK_COLOR['water_exit'])

        self.root.update()
        if self.ui.running:
            self.ui.toogle_start_stop()
    
    def load2(self):
        filetypes=(('json files', '*.json'),('All files', '*.*'))
        initialdir='/home/christoph/Own_projects/RisingWater/worlds' 
        filename = filedialog.askopenfilename(title='Open a file', filetypes=filetypes, initialdir=initialdir)
        self.load(filename)
        pass
    
    def draw(self):
        for x in range (self.extend[X]):
            for y in range (self.extend[Y]):
                block = self.blocks[(x,y)]
                self.canvas.itemconfig(block.pol_ref, fill = constant.BLOCK_COLOR[block.type])
        for pos in self.water_exits:
            self.canvas.itemconfig(self.blocks[pos].pol_ref, fill = constant.BLOCK_COLOR['water_exit'])
        for pos in self.water_entries:
            self.canvas.itemconfig(self.blocks[pos].pol_ref, fill = constant.BLOCK_COLOR['water_entry'])
        pass

    def analyse(self):
        self.waterbodies = []
        self.watercolumns = {}
        for pos, block in self.blocks.items():
            if block.type != 'water':
                continue
            if pos in Waterbody.register:
                continue
            else:
                new_wb_id = Waterbody.get_next_id()
                waterbody = Waterbody(new_wb_id)
                self.waterbodies.append(waterbody)
                Waterbody.register.append(pos)
                block.waterbody = waterbody
                waterbody.blocks.append(block)
                self.add_neighbors_to_waterbody(block, waterbody)
                waterbody.set_extend()
            pass
        self.identify_watercolumns()

    def identify_watercolumns(self):
        inside_column = False
        current_column = None
        for x in range (self.extend[X]):
            for y in range (self.extend[Y]):
                block = self.blocks[(x,y)]
                if block.type == 'water':
                    if inside_column == False:
                        inside_column = True
                        current_column = (x,y)
                        new_wc = {'start': block, 'foot': None, 'swapped': False}
                        self.watercolumns[(x,y)] = new_wc
                        if y not in block.waterbody.watercolumns:
                            block.waterbody.watercolumns[y] = []
                        block.waterbody.watercolumns[y].append(new_wc)
                if block.type in ['air', 'earth'] or y == self.extend[Y]-1:
                    if inside_column == True:
                        self.watercolumns[current_column]['foot'] = block
                        inside_column = False
                        current_column = None
        pass

    def add_neighbors_to_waterbody(self, block, waterbody):
        neighbors = block.get_neighbors()
        for neighbor in neighbors:
            if neighbor.type == 'air' and neighbor.get_pos() not in waterbody.adjacent_air_blocks.keys():
                waterbody.adjacent_air_blocks[neighbor.get_pos()] = {'block': neighbor, 'swapped': False}
                air_topology = neighbor.get_air_block_topology()
                waterbody.adjacent_air_blocks[neighbor.get_pos()]['topology'] = air_topology
            elif neighbor.type == 'water' and neighbor.get_pos() not in Waterbody.register:
                neighbor.waterbody = waterbody
                waterbody.blocks.append(neighbor)
                Waterbody.register.append(neighbor.get_pos())
                self.add_neighbors_to_waterbody(neighbor, waterbody)
    
    def move_blocks(self):
        for waterbody in self.waterbodies:
            levels = list(waterbody.watercolumns.keys())
            levels.sort()
            air_blocks = waterbody.filter_air_blocks()
            for _, columns in waterbody.watercolumns.items():   
                for column in columns:
                    if column['foot'].type == 'air' and True == rnd.choice([True, True, False]):
                        self.swap(column['start'], column['foot'])
                        column['start'].waterbody.adjacent_air_blocks[column['foot'].get_pos()]['swapped'] = True
                        column['swapped'] = True
            for level in levels:
                columns = waterbody.watercolumns[level]
                rnd.shuffle(columns)
                for column in columns:
                    if column['swapped'] == False:
                        waterbody = column['start'].waterbody

                        air_blocks = {pos:block for pos, block in air_blocks.items() if pos[1] > column['start'].get_pos()[1]}
                        air_blocks = {pos:block for pos, block in air_blocks.items() if block['swapped'] == False}
                        
                        air_pos = None
                        if True == rnd.choice([True,False]):
                           air_pos = self.get_nearest_block(column['start'].get_pos(), air_blocks)
                        elif bool(air_blocks):
                            air_pos = rnd.choice(list(air_blocks.keys()))
                        if air_pos == None:
                            continue
                        air_block = air_blocks[air_pos]
                        self.swap(column['start'], air_block['block'])
                        air_block['swapped'] = True
                        column['swapped'] = True

            for entry in self.water_entries:
                self.blocks[entry].type = 'water'
            for entry in self.water_exits:
                self.blocks[entry].type = 'air'
    def swap(self, block_a, block_b):
        temp = block_a.type
        block_a.type = block_b.type
        block_b.type = temp
    
    def get_nearest_block(self, pos_fixed, positions):
        min_dist = np.Inf
        nearest_pos = None
        for pos,_ in positions.items():
            dist = math.hypot(pos[X]-pos_fixed[X], pos[Y]-pos_fixed[Y])
            if dist == min_dist:
                if True == rnd.choice([True,False]):
                    nearest_pos = pos
            if dist < min_dist:
                min_dist = dist
                nearest_pos = pos
        return nearest_pos

    def update_blocks(self):
        self.draw()

class Block:
    def __init__(self, type, pos_x, pos_y, pol_ref, world_ref):
        self.type = type
        self.pol_ref = pol_ref
        self.pos_x = pos_x
        self.pos_y = pos_y
        self.world = world_ref
        self.waterbody = None
    
    def get_neighbors(self):
        neighbors = []
        if self.pos_x > 0:
            neighbors.append(self.world.blocks[(self.pos_x-1, self.pos_y)])
        if self.pos_y > 0:
            neighbors.append(self.world.blocks[(self.pos_x, self.pos_y-1)])
        if self.pos_x < self.world.extend[X]-1:
            neighbors.append(self.world.blocks[(self.pos_x+1, self.pos_y)])
        if self.pos_y < self.world.extend[Y]-1:
            neighbors.append(self.world.blocks[(self.pos_x, self.pos_y+1)])

        return neighbors

    def get_air_block_topology(self):
        neighbors = {}
        for neighbor in self.get_neighbors():
            neighbors[(neighbor.pos_x, neighbor.pos_y)] = neighbor
        if(self.pos_x, self.pos_y-1) in neighbors:
            if neighbors[(self.pos_x, self.pos_y-1)].type == 'water':
                return "below"
        if(self.pos_x+1, self.pos_y) in neighbors:
            if neighbors[(self.pos_x+1, self.pos_y)].type == 'water':
                return "side"
        if(self.pos_x-1, self.pos_y) in neighbors:
            if neighbors[(self.pos_x-1, self.pos_y)].type == 'water':
                return "side"
        return "above"
    
    def get_pos(self):
        return (self.pos_x, self.pos_y)
    
    def to_json(self):
        return {self.get_pos(): {'type': self.type}}

class Waterbody:
    def __init__(self, id):
        self.id = id
        self.blocks = []
        self.top_level = constant.EXTEND_Y -1
        self.low_level = 0
        self.adjacent_air_blocks = {}
        self.lowest_adjacent_air = 0
        self.is_stable = True
        self.watercolumns = {}

    register = []
    next_id = 0
    def get_next_id():
        Waterbody.next_id +=1
        return Waterbody.next_id
    
    def set_extend(self):
        for block in self.blocks:
            if block.pos_y < self.top_level:
                self.top_level = block.pos_y
            if block.pos_y > self.low_level:
                self.low_level = block.pos_y

    def get_structure(self):
        water_blocks = {}
        air_blocks = {}
        for block in self.blocks:
            if block.pos_y not in water_blocks:
                water_blocks[block.pos_y] = []
            water_blocks[block.pos_y].append({'block': block, 'moved': False})
        for _, block in self.adjacent_air_blocks.items():
            if block.pos_y not in air_blocks:
                air_blocks[block.pos_y] = []
            air_blocks[block.pos_y].append(block)

        return water_blocks, air_blocks
    
    def filter_air_blocks(self):
        blocks_to_remove = []
        air_blocks = self.adjacent_air_blocks
        air_blocks = {pos:block for pos, block in air_blocks.items() if pos[1] > self.top_level}
        below_blocks = [pos for pos, block in air_blocks.items() if block['topology'] == 'below']
        side_blocks = [pos for pos, block in air_blocks.items() if block['topology'] == 'side']
        for pos, air_block in air_blocks.items():
            if air_block['topology'] in ['side', 'above']:
                for below_pos in below_blocks:
                    dist = math.hypot(below_pos[X]-air_block['block'].pos_x, below_pos[Y]-air_block['block'].pos_y)
                    if dist < 3:
                        blocks_to_remove.append(pos)
            if air_block['topology'] == 'above':
                for side_pos in side_blocks:
                    dist = math.hypot(side_pos[X]-air_block['block'].pos_x, side_pos[Y]-air_block['block'].pos_y)
                    if dist < 8:
                        blocks_to_remove.append(pos)

        blocks_to_remove = list(set(blocks_to_remove)) #get unique values
        for pos in blocks_to_remove:
            air_blocks.pop(pos)
        
        return air_blocks

    # refactoring
    # (convert to exe)

    # weniger tiefe / mehr funktionen
    # Kommentare