import constant
import json
X = 0
Y = 1

class UI:
    def __init__(self, root, canvas, speed):
        self.root = root
        self.canvas = canvas
        self.speed = speed
        self.world = None
        self.running = True
        self.pointer = [0,0]

    def main(self):    
        if self.running:
            block_ref = f'{self.pointer[X]}/{self.pointer[Y]}'
            pol_ref = self.world.blocks[block_ref].pol_ref 
            self.world.blocks[block_ref].type = "air"
            self.canvas.itemconfig(pol_ref, fill =constant.BLOCK_COLOR["air"])

            if self.pointer[X] < (self.world.extend[X] -1):
                self.pointer[X] += 1
            elif self.pointer[X] == (self.world.extend[X] - 1):
                self.pointer[X] = 0
                self.pointer[Y] += 1
            if self.pointer[Y] == (self.world.extend[Y]):
                self.pointer[Y] = 0

            ref = self.world.blocks[f'{self.pointer[X]}/{self.pointer[Y]}'].pol_ref
            self.canvas.itemconfig(ref, fill ="red")
            self.root.update()
        self.root.after(self.get_speed(), self.main)

    def start(self):
        self.running = True
    
    def get_speed(self):
        control_val = self.speed.get()
        speed = (constant.SPEED_STEPS - control_val + 1) ** 3
        return speed

    def stop(self):
        self.running = False

class World:
    def __init__(self, extend, blocks = {}):
        self.extend = extend
        self.blocks = blocks
        self.drawing = False
        self.root = None
        self.canvas = None
        self.selected_block_type = "earth"
    
    def set_selected_block_type(self, type):
        self.selected_block_type = type

    def generate(self, canvas):
        block_size = constant.BLOCK_SIZE
        for x in range (self.extend[0]):
            for y in range (self.extend[1]):
                start_x = constant.CANVAS_START + (x * block_size)
                start_y = constant.CANVAS_START + (y * block_size)
                points = [start_x, start_y, start_x + block_size, start_y, start_x + block_size, start_y + block_size, start_x, start_y +block_size]
                ref = canvas.create_polygon(points, fill="white", outline="black")
                block = Block("air", ref)
                self.blocks[f"{x}/{y}"] = block

    def save(self):
        with open('world.json', 'w') as json_file:
            output = {key: value.__dict__ for key, value in self.blocks.items()}
            json.dump(output, json_file)

    def load(self):
        with open('world.json', 'r') as json_file:
            input = json.load(json_file)
            for key, block in input.items():
                self.blocks[key].type = block['type']
                color = constant.BLOCK_COLOR[block['type']]
                self.canvas.itemconfig(self.blocks[key].pol_ref, fill =color)
            self.root.update()

class Block:
    def __init__(self, type, pol_ref):
        self.type = type
        self.pol_ref = pol_ref
        