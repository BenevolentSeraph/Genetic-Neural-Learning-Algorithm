from random import randint
from time import sleep
import pygame

FPS = 50
pass_size = 2
pass_side = 1

def cap(num,minimum,maximum):
    if num < minimum: return minimum
    elif num > maximum: return maximum
    else: return num

# Visual display object for better comprehension.
class display:
    def __init__(self,size=500,gridsize=10,bg=(0,0,0)):
        self.window = pygame.display.set_mode((size,size))
        self.window.fill(bg)
        self.size = size
        self.bg = bg
        self.frame = 0
        self.gridsize = gridsize
        self.clock = pygame.time.Clock()
    def update(self,board=None):
        global parents, FPS, cells, pass_size, pass_side
        self.frame += 1
        pygame.display.set_caption(f"FPS: {FPS} | Frame: {self.frame%50} | Generation: {int(self.frame/50)}")
        self.window.fill(self.bg)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.display.quit()
                pygame.quit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_DOWN:
                    FPS -= 10
                elif event.key == pygame.K_UP:
                    FPS += 10
                if event.key == pygame.K_w:
                    cells = cap(cells+50,50,500)
                elif event.key == pygame.K_s:
                    cells = cap(cells-50,50,500)
                if event.key == pygame.K_i:
                    pass_size = cap(pass_size+1,2,25)
                elif event.key == pygame.K_k:
                    pass_size = cap(pass_size-1,2,25)
                if event.key == pygame.K_t:
                    pass_side = cap(pass_side+1,1,4)
                elif event.key == pygame.K_g:
                    pass_side = cap(pass_side-1,1,4)
        for y in range(self.gridsize):
            for x in range(self.gridsize):
                rect = pygame.Rect(x*self.size/self.gridsize, y*self.size/self.gridsize, self.size/self.gridsize, self.size/self.gridsize)
                if board == None:
                    pygame.draw.rect(self.window, (255,0,0), rect, 1)
                else:
                    if board.get([x,y]) == 1:
                        pygame.draw.rect(self.window, (0,255,0), rect, 1)
                    else:
                        pygame.draw.rect(self.window, (255,0,0), rect, 1)
        pygame.display.update()
        self.clock.tick(int(FPS))
        return self.frame

class universe:
    def __init__(self,size):
        self.size = size
        self.space = []
        for y in range(size):
            row = []
            for x in range(size):
                row.append(0)
            self.space.append(row)
        #self.show()
    def get(self,pos):
        try:
            if pos[0] >= self.size or pos[1] >= self.size or pos[0] < 0 or pos[1] < 0: raise Exception("Overflow")
            return self.space[pos[1]][pos[0]]
        except Exception as e:
            return 2
    def set(self,pos,value):
        try:
            self.space[pos[1]][pos[0]] = value
            return self.get(pos)
        except:
            return 0
    def show(self):
        #print(self.space)
        for row in self.space:
            string = ""
            for cell in row:
                string += str(cell)
            print(string)
        print()
    
class organism:
    LR = 100 # learning rate
    def __init__(self,pos,board,weights=[0,0,0,0],bias=[0,0,0,0]):
        if weights == [0,0,0,0]:
            self.weights = []
            for x in range(4):
                self.weights.append(randint(0,self.LR)/self.LR)
        else:
            self.weights = weights
        if bias == [0,0,0,0]:
            self.bias = []
            for x in range(4):
                self.bias.append(randint(0,self.LR)/self.LR)
        else:
            self.bias = bias
        self.pos = pos
        self.board = board
        self.board.set(pos,1)
    def step(self):
        # Input Layer
        right_spot = self.board.get([self.pos[0]+1,self.pos[1]])
        left_spot = self.board.get([self.pos[0]-1,self.pos[1]])
        down_spot = self.board.get([self.pos[0],self.pos[1]+1])
        up_spot = self.board.get([self.pos[0],self.pos[1]-1])
        # Hidden Layer (adding the weights and bias)
        right = right_spot*self.weights[0]+self.bias[0]
        left = left_spot*self.weights[1]+self.bias[1]
        down = down_spot*self.weights[2]+self.bias[2]
        up = up_spot*self.weights[3]+self.bias[3]
        # Actions
        if right > 0.8 and right_spot == 0:
            # move right
            self.board.set([self.pos[0]+1,self.pos[1]],1)
            self.board.set([self.pos[0],self.pos[1]],0)
            self.pos = [self.pos[0]+1,self.pos[1]]
            #print(self,"moved right")
        elif left > 0.8 and left_spot == 0:
            # move left
            self.board.set([self.pos[0]-1,self.pos[1]],1)
            self.board.set([self.pos[0],self.pos[1]],0)
            self.pos = [self.pos[0]-1,self.pos[1]]
            #print(self,"moved left")
        elif down > 0.8 and down_spot == 0:
            # move down
            self.board.set([self.pos[0],self.pos[1]+1],1)
            self.board.set([self.pos[0],self.pos[1]],0)
            self.pos = [self.pos[0],self.pos[1]+1]
            #print(self,"moved down")
        elif up > 0.8 and up_spot == 0:
            # move up
            self.board.set([self.pos[0],self.pos[1]-1],1)
            self.board.set([self.pos[0],self.pos[1]],0)
            self.pos = [self.pos[0],self.pos[1]-1]
            #print(self,"moved up")
        else:
            # wait
            pass

MR = 10 # Mutation Rate (1/MR)
MS = 10 # Mutation Strength (%)
parents = []
organisms = []
cells = 300
size = 50
dis = display(size=600,gridsize=size)
while True:
    # Create/Recreate the map with the new organisms (from their parents if they're available).
    b = universe(size)
    x = 0
    while x < cells:
        pos = [randint(0,size-1),randint(0,size-1)]
        if b.get(pos) == 0:
            if len(parents) == 0:
                # Randomly generate organisms if there are no parents.
                organisms.append(organism(pos,b))
            else:
                # Generate offspring based on the parents.
                p = parents[randint(0,len(parents)-1)]
                newweights = list(p.weights)
                for y in range(len(newweights)):
                    if randint(1,MR) == MR:
                        newweights[y] += cap(randint(-MS,MS)/100,0,1)
                newbias = list(p.bias)
                for y in range(len(newbias)):
                    if randint(1,MR) == MR:
                        newbias[y] += cap(randint(-MS,MS)/100,0,1)
                organisms.append(organism(pos,b,weights=newweights,bias=newbias))
            x += 1
    # Run the simulation 50 times (5 seconds if the display is on).
    for x in range(50):
        print(f"FPS: {FPS} | Frame: {dis.frame%50} | Generation: {int(dis.frame/50)}")
        print(f"Survivors: {len(parents)} | Organisms: {cells} | Map %: {pass_size} | Side: {pass_side}")
        for c in organisms:
            c.step()
        dis.update(board=b)
    # Check which organisms passed
    parents = []
    b = universe(size)
    for x in organisms:
        # Reproduction Condition (They get to reproduce if they're on the right half of the map. Food scarcity & mates are the condition in real life.)
        if pass_side == 1:
            if x.pos[0] > size-int(size/pass_size):
                parents.append(x)
        elif pass_side == 2:
            if x.pos[0] < int(size/pass_size):
                parents.append(x)
        elif pass_side == 3:
            if x.pos[1] > size-int(size/pass_size):
                parents.append(x)
        elif pass_side == 4:
            if x.pos[1] < int(size/pass_size):
                parents.append(x)
    organisms = []
