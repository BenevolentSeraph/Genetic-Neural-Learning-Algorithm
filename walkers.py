import neural
import pygame
import random
from time import sleep

class display:
    def __init__(self,size=500,gridsize=50,bg=(0,0,0),FPS=50,showrate=1):
        self.window = pygame.display.set_mode((size,size))
        self.window.fill(bg)
        self.size = size
        self.bg = bg
        self.frame = 0
        self.gridsize = gridsize
        self.clock = pygame.time.Clock()
        self.FPS = FPS
        self.showrate = showrate
    def update(self,board=None):
        global parents, ticks
        self.frame += 1
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.display.quit()
                pygame.quit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_DOWN:
                    self.FPS -= 10
                elif event.key == pygame.K_UP:
                    self.FPS += 10
        pygame.display.set_caption(f"FPS: {self.FPS} | Frame: {self.frame%ticks} | Generations/Show: {self.showrate} | Generation: {int(self.frame/ticks)} | Survivors: {len(parents)}")
        if int(self.frame / ticks) % self.showrate == 0:
            self.window.fill(self.bg)
            for y in range(self.gridsize):
                for x in range(self.gridsize):
                    rect = pygame.Rect(x*self.size/self.gridsize, y*self.size/self.gridsize, self.size/self.gridsize, self.size/self.gridsize)
                    if board == None:
                        pygame.draw.rect(self.window, (255,255,255), rect, 1)
                    else:
                        if board.get([x,y]) == 1:
                            pygame.draw.rect(self.window, (0,255,0), rect, 1)
                        else:
                            pygame.draw.rect(self.window, (255,0,0), rect, 1)
            pygame.display.update()
            self.clock.tick(self.FPS)
        return self.frame

class universe:
    def __init__(self,size):
        self.size = size
        self.space = []
        for y in range(size):
            row = []
            for x in range(size):
                row.append(-1)
            self.space.append(row)
        #self.show()
    def get(self,pos):
        try:
            if pos[0] >= self.size or pos[1] >= self.size or pos[0] < 0 or pos[1] < 0: raise Exception("Overflow")
            return self.space[pos[1]][pos[0]]
        except Exception as e:
            return 1
    def set(self,pos,value):
        try:
            self.space[pos[1]][pos[0]] = value
            return self.get(pos)
        except Exception as e:
            #print(e)
            return 0

class organism:
    def __init__(self,pos,board,inputs=[0],brain=None):
        self.inputs = inputs
        if brain == None:
            self.brain = neural.brain(inputs=self.inputs,layers=[50,20,5])
        else:
            self.brain = brain
        self.pos = pos
        self.board = board
        self.board.set(pos,1)
    def move(self,pos):
        if self.board.get(pos) != 1:
            pos = [neural.cap(pos[0],0,self.board.size-1),neural.cap(pos[1],0,self.board.size-1)]
            self.board.set(self.pos,-1)
            self.board.set(pos,1)
            self.pos = pos
            return True
        return False
    def tick(self):
        if self.brain == None:
            raise Exception("No Brain")
        self.inputs = []
        self.inputs.append(self.pos[0])
        self.inputs.append(self.pos[1])
        sight = 10
        for y in range(sight):
            for x in range(sight):
                input_pos = [self.pos[0]-int(sight/2),self.pos[1]-int(sight/2)]
                if [self.pos[0]-int(x/2),y] != self.pos:
                    self.inputs.append(self.board.get([x,y]))
                else:
                    self.inputs.append(3)
        self.inputs.append(self.pos[0]/size)
        self.inputs.append(self.pos[1]/size)
        self.brain.inputs = self.inputs
        action = self.brain.output_action()[0]
        if action == 1: # move right
            self.move([self.pos[0]+1,self.pos[1]])
        elif action == 2: # move left
            self.move([self.pos[0]-1,self.pos[1]])
        elif action == 3: # move down
            self.move([self.pos[0],self.pos[1]+1])
        elif action == 4: # move up
            self.move([self.pos[0],self.pos[1]-1])
        else: # wait
            pass
        return action
    def replicate(self,pos,board):
        return organism(pos,board,brain=self.brain.replicate())

if __name__ == "__main__":
    parents = []
    organisms = []
    stray_chance = 100
    population = 100
    ticks = 50
    size = 50
    winsize = 600
    board = universe(size)
    window = display(size=winsize,gridsize=size,showrate=3)
    while True:
        # Generating & Populating the map
        board = universe(size)
        organisms = []
        while len(organisms) < population:
            pos = [random.randint(0,size-1),random.randint(0,size-1)]
            if board.get(pos) != 1:
                parent_chance = random.randint(1,stray_chance)
                if len(parents) > 0 and parent_chance != stray_chance:
                    # Generate based on parents
                    if len(organisms) < len(parents):
                        new_organism = parents[len(organisms)].replicate(pos,board)
                    else:
                        new_organism = parents[random.randint(0,len(parents)-1)].replicate(pos,board)
                    organisms.append(new_organism)
                else:
                    # Randomly Generate
                    organisms.append(organism(pos,board))
        # Start the simulation
        for x in range(ticks):
            for y in range(len(organisms)):
                organisms[y].tick()
            window.update(board=board)
        # Filter out the survivors
        parents = []
        for x in organisms:
            if x.pos[0] > size-int(size/4) and x.pos[1] > size-int(size/4):
                x.board.set(x.pos,0)
                parents.append(x)
