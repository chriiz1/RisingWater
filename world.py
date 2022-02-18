from __future__ import annotations
from ast import Str
from logging import critical
import os
import constants
import json
import math
import numpy as np
import random as rnd
import tkinter as tk
from tkinter import filedialog

X = 0
Y = 1

class Block:
    def __init__(self, type: Str, subtype: Str, pos_x: int, pos_y: int, pol_ref: int, world_ref: World):
        self.type = type
        self.subtype = subtype
        self.pol_ref = pol_ref
        self.pos_x = pos_x
        self.pos_y = pos_y
        self.world = world_ref
        self.waterbody = None
        self.swapped = False
    
    def get_neighbors(self, direction = None):
        '''
        returns the neighbors of a block in terms of the "neumann neighborhood"
        '''
        neighbors = []
        if not self.is_at_left():
            neighbors.append(self.world.blocks[(self.pos_x-1, self.pos_y)])
        if not self.is_at_top():
            neighbors.append(self.world.blocks[(self.pos_x, self.pos_y-1)])
        if not self.is_at_right():
            neighbors.append(self.world.blocks[(self.pos_x+1, self.pos_y)])
        if not self.is_at_bottom():
            neighbors.append(self.world.blocks[(self.pos_x, self.pos_y+1)])

        return neighbors

    def is_at_bottom(self):
        return self.pos_y == self.world.extend[Y]-1

    def is_at_top(self):
        return self.pos_y == 0

    def is_at_left(self):
        return self.pos_x == 0

    def is_at_right(self):
        return self.pos_x == self.world.extend[X] -1

    def get_air_block_topology(self):
        '''
        checks where an air block is in relation to surrounding water blocks
        '''
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
    
class Watercolumn:
    def __init__(self, head, foot):
        self.head = head
        self.foot = foot
        self.swapped = False

class Waterbody:
    def __init__(self, first_block: Block = None, world: World = None):
        self.id = Waterbody.next_id
        self.blocks = {}
        self.top_level = constants.EXTEND_Y -1
        self.low_level = 0
        self.surrounding_air_blocks = {}
        self.lowest_surrounding_air = 0
        self.block_register = []
        self.watercolumns = {}
        
        Waterbody.next_id +=1
        self.blocks[first_block.get_pos()] = first_block
        world.block_register.append(first_block.get_pos())
        first_block.waterbody = self
        world.add_neighbors_to_waterbody(first_block, self)
        self.set_vertical_extend()
    
    next_id = 0
    
    def set_vertical_extend(self):
        for pos in self.blocks.keys():
            if pos[Y] < self.top_level:
                self.top_level = pos[Y]
            if pos[Y] > self.low_level:
                self.low_level = pos[Y]
    
    def sort_blocks(self):
        keys = list(self.blocks.keys())
        keys.sort(key = lambda x: x[1]) 
        new_blocks = {}
        for key in keys:
            new_blocks[key] = self.blocks[key]
        self.blocks = new_blocks
    
    def check_block_to_remove(self, pos, other_air_blocks, other_air_blocks_type):
        '''
        checks if an air block is within the critical distance to another 
        air block with a higher priority (Reason: Inhibit water movement)
        '''
        if other_air_blocks == {}:
            return None
        for other_pos in other_air_blocks:
            dist_x = other_pos[X]-pos[X]
            dist_y = other_pos[Y]-pos[Y]
            total_dist = math.hypot(dist_x, dist_y)
            critical_dist = 0
            if other_air_blocks_type == 'below':
                critical_dist = constants.AIR_BLOCK_BELOW_CRITICAL_DISTANCE 
            elif other_air_blocks_type == 'side':
                critical_dist = constants.AIR_BLOCK_SIDE_CRITICAL_DISTANCE
            if total_dist < critical_dist:
                return True
        return False   
    
    def filter_air_blocks(self): 
        '''
        Filter air blocks depending on their topology with water blocks
        '''
        blocks_to_remove = []
        air_blocks = self.surrounding_air_blocks
        below_blocks = [pos for pos, block in air_blocks.items() if block['topology'] == 'below' 
                        and block['block'].swapped == False]
        side_blocks = [pos for pos, block in air_blocks.items() if block['topology'] == 'side' 
                        and block['block'].swapped == False]

        for pos, air_block in air_blocks.items():
            remove = False
            if air_block['topology'] in ['side', 'above']:
                remove = self.check_block_to_remove(pos, below_blocks, 'below')
                    
            if air_block['topology'] == 'above':
                remove = self.check_block_to_remove(pos, side_blocks, 'side')
            
            blocks_to_remove.append(pos) if remove is True else None

        for pos in blocks_to_remove:
            air_blocks.pop(pos)
        
        return air_blocks

    def identify_watercolumns(self): 
        '''
        organzises a waterbody into single watercolumns
        '''
        for pos, block in self.blocks.items():
            if pos in self.block_register:
                continue

            self.block_register.append(pos)
            foot = None
            y = pos[Y] 
            
            # starting from the head block, go downwards until the end of the column
            while y < constants.EXTEND_Y - 1:
                y += 1
                new_pos = (pos[X], y)
                if (new_pos) in self.blocks.keys():
                    self.block_register.append(new_pos)
                    continue
                else:
                    foot = block.world.blocks[new_pos]
                    break

            if foot == None:
                foot = block

            new_water_column = Watercolumn(head=block, foot=foot)
            self.watercolumns[pos] = new_water_column

class World:
    def __init__(self, extend = [constants.EXTEND_X, constants.EXTEND_Y], blocks = {}):
        import user_interface

        self.root = None
        self.ui = user_interface.UI
        self.extend = extend
        self.blocks = blocks
        self.drawing = False
        self.canvas = None
        self.waterbodies = []
        self.block_register = []
        self.watercolumns = {}
    
    def generate_empty_world(self, canvas):
        block_size = constants.BLOCK_SIZE
        for x in range (self.extend[X]):
            for y in range (self.extend[Y]):
                start_x = constants.CANVAS_START + (x * block_size)
                start_y = constants.CANVAS_START + (y * block_size)
                points = [start_x, start_y, start_x + block_size, start_y,
                        start_x + block_size, start_y + block_size, start_x,
                        start_y + block_size]
                fill = constants.BLOCK_COLOR["air"]
                ref = canvas.create_polygon(points, fill=fill, outline="black")
                block = Block("air", "air", x, y, ref, self)
                self.blocks[(x,y)] = block

    def prepare_save_file(self):
        output = {str(key): {'type': value.type, 'subtype': value.subtype}
                for key, value in self.blocks.items()}
        return output

    def save_default(self):
        file = os.path.join(constants.SAVE_FOLDER, 'default.json')
        with open(file, 'w') as json_file:
            output = self.prepare_save_file()
            json.dump(output, json_file)
    
    def save_as(self):
        f = filedialog.asksaveasfile(mode='w', defaultextension=".json",
                initialdir=constants.SAVE_FOLDER,filetypes=[("json", "*.json")])
        if f is None: 
            return
        output = self.prepare_save_file()
        text2save = json.dumps(output)
        f.write(text2save)
        f.close() 

    def load_default(self, filename = 'default.json'):
        file = os.path.join(constants.SAVE_FOLDER, filename)
        with open(file, 'r') as json_file:
            input = json.load(json_file)
            for key, block in input.items():
                key = eval(key)
                self.blocks[key].type = block['type'] 
                self.blocks[key].subtype = block['subtype']
                color = constants.BLOCK_COLOR[block['subtype']]
                self.canvas.itemconfig(self.blocks[key].pol_ref, fill = color)

        self.root.update()
        if self.ui.running:
            self.ui.toogle_start_stop()
    
    def load(self):
        filetypes=(('json files', '*.json'),('All files', '*.*'))
        filename = filedialog.askopenfilename(title='Open a file',
                filetypes=filetypes, initialdir=constants.SAVE_FOLDER)
        self.load_default(filename)
    
    def draw(self):
        for x in range(self.extend[X]):
            for y in range (self.extend[Y]):
                block = self.blocks[(x,y)]
                fill = constants.BLOCK_COLOR[block.subtype]
                self.canvas.itemconfig(block.pol_ref, fill = fill)

    def organise_water_blocks(self): 
        '''
        organise all water blocks into waterbodies and watercolumns
        '''
        self.identify_waterbodies()
        waterbody: Waterbody
        for waterbody in self.waterbodies:
            waterbody.sort_blocks()
            waterbody.identify_watercolumns()

    def identify_waterbodies(self):
        self.block_register = []
        self.waterbodies = []
        for pos, block in self.blocks.items():
            if block.type != 'water':
                continue
            if pos in self.block_register:
                continue
            else:
                waterbody = Waterbody(block, self) # the inital block is handed over
                self.waterbodies.append(waterbody)

    def add_neighbors_to_waterbody(self, block: Block, waterbody: Waterbody):
        '''
        Starting from one waterblock, add all connected waterblocks 
        and the surrounding air blocks to a waterbody 
        The function does that in a recursive way
        '''
        for neighbor in block.get_neighbors():
            key = neighbor.get_pos()
            if neighbor.type == 'water' and key not in self.block_register:
                neighbor.waterbody = waterbody
                waterbody.blocks[key] = neighbor
                self.block_register.append(key)
                self.add_neighbors_to_waterbody(neighbor, waterbody)
            elif neighbor.type == 'air' and key not in waterbody.surrounding_air_blocks.keys():
                waterbody.surrounding_air_blocks[key] = {'block': neighbor}
                air_topology = neighbor.get_air_block_topology()
                waterbody.surrounding_air_blocks[key]['topology'] = air_topology
    
    def move_blocks(self):
        '''
        the core function for the movement of the water blocks
        '''
        # order waterbodies by their length: bigger waterbodies can move earlier
        self.waterbodies.sort(key = lambda x: len(x.blocks), reverse=True)

        for waterbody in self.waterbodies:
            air_blocks = waterbody.filter_air_blocks()

            air_foot_columns = [column for _, column in waterbody.watercolumns.items() 
                                if column.foot.type == 'air']
            for column in air_foot_columns:
                if True == rnd.choice([True, True, False]): 
                    self.swap(column.head, column.foot)
                    column.swapped = True

            for head_pos, column in waterbody.watercolumns.items():
                if column.swapped == False:
                    air_blocks = {pos:block for pos, block in air_blocks.items() 
                                if pos[Y] > head_pos[Y] and block['block'].swapped == False}
                    air_pos = None

                    # Choose nearest air block with a certain probability
                    if True == rnd.choice([True,False]):
                        air_pos = self.get_nearest_block(column.head.get_pos(), air_blocks)
                    
                    # Otherwise randomly choose an air block
                    elif bool(air_blocks):
                        air_pos = rnd.choice(list(air_blocks.keys()))

                    if air_pos == None:
                        continue

                    air_block = air_blocks[air_pos]
                    self.swap(column.head, air_block['block'])
                    air_block['swapped'] = True
                    column.swapped = True

        for _, block in self.blocks.items():
            block.swapped = False

    def swap(self, block_a: Block, block_b: Block):
        '''
        swap the attributes of two blocks
        '''
        if block_a.subtype == 'water_entry' and block_b.subtype == 'water_exit':
            return
        elif block_a.subtype == 'water_entry':
            block_b.type = block_a.type
            block_b.subtype = block_a.type
        elif block_b.subtype == 'water_exit':
            block_a.type = block_b.type
            block_a.subtype = block_b.type
        else:
            temp_type = block_a.type
            temp_subtype = block_a.subtype
            block_a.type = block_b.type
            block_a.subtype = block_b.subtype
            block_b.type = temp_type
            block_b.subtype = temp_subtype
        block_a.swapped = True
        block_b.swapped = True

    def get_nearest_block(self, pos_fixed, positions):
        '''
        get the nearest block starting from a fixed position
        '''
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