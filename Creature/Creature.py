import numpy as np
from os import system, popen
import time
from copy import deepcopy

EPOCH_DELAY = 0.01
CREATURE_POPULATION = 9
DIMENSION_SIZE = 30

def euclid(x1,y1,cor):
    #print cor
    #print x1, y1
    return sorted([
        ( 
            (  (x-x1)**2 + (y-y1)**2  ) ** 0.5, (x, y) 
        ) 
            for x,y in cor], key = lambda x: x[0])

def poisson_dist(nibl_loc, nio_no=1):
    return np.random.poisson(nibl_loc, (nio_no,2))


class Field:
    def __init__(self, x=11, y=11, no=2, nibbles=10, n_stat=False):
        self.x = x
        self.y = y
        self.no = no
        self.field = np.zeros((x, y))
        self.nibl_loc=(np.random.randint(0,x-1), np.random.randint(0,y-1))
        self.no_n = int(round(nibbles))
        self.nibbles = poisson_dist(self.nibl_loc, self.no_n)
        self.nibble_static = n_stat
        for n_x, n_y in self.nibbles:
            if n_x < self.x and n_y < self.y:
                self.field[n_x][n_y] = -1

    def produce(self):
        if self.nibble_static == False:
            no = self.no_n - len(self.field[self.field == -1])
            if no > 0:
                n_x, n_y = zip(*poisson_dist(self.nibl_loc, no))
                self.nibbles = self.nibbles.tolist()
                for x,y in zip(n_x, n_y):
                    if x < self.x and y < self.y:
                        self.nibbles.append([x, y])
                        self.field[x][y] = -1
                self.nibbles = np.array(self.nibbles)
    
    def __str__(self):
        tmpf = np.array(self.field, dtype = str)
        for x in range(self.x):
            for y in range(self.y):
                if tmpf[x][y] == '0.0':
                    tmpf[x][y] = '.'
                elif tmpf[x][y] == '-1.0':
                    tmpf[x][y] = '\x1b[93mo\x1b[0m'
                elif '0.0' < tmpf[x][y] < '1.0':
                    tmpf[x][y] = '\x1b[91mx\x1b[0m'

        st = ''
        for x in tmpf:
            for y in x:
                st += '%s ' % y
            st += '\n'

        return st

class Creature:
    def __init__(self, field, x=-1, y=-1):
        self.Field = field
        self.field = self.Field.field
        self.f_x, self.f_y = self.field.shape
        self.x = np.random.randint(0,self.f_x-1) if x == -1 else x
        self.y = np.random.randint(0,self.f_y-1) if y == -1 else y
        self.closest_nibbles = euclid(self.x, self.y, self.Field.nibbles) 
        self.n_x, self.n_y = self.closest_nibbles[0][1]
        self.fitness = 0.0
        self.total_time = 0.0

        
        self.id = np.random.random()
        self.field[self.x][self.y] = self.id


    def safety_move(self):
        if self.x < 0:
            self.x = 0
        elif self.x >= self.f_x:
            self.x = self.f_x-2

        
        if self.y < 0:
            self.y = 0
        elif self.y >= self.f_y:
            self.y = self.f_y-2
        

        self.eat_nibble()

    def is_at_nibble(self): return [self.x, self.y] in self.Field.nibbles

    def eat_nibble(self):
        self.Field.nibbles = self.Field.nibbles.tolist()
        if self.is_at_nibble():
            self.Field.nibbles.remove([self.x, self.y])
        self.Field.nibbles = np.array(self.Field.nibbles)

    def normal_move(self):
        
        self.field[self.x][self.y] = 0 

        move_coor = [self.x, self.y]

        if self.x > self.n_x and self.x > 0:
            move_coor[0] -= 1
        elif self.x < self.n_x and self.x < self.f_x:
            move_coor[0] += 1
        else:
            pass
                
        if self.y > self.n_y and self.y > 0:
            move_coor[1] -= 1
        elif self.y < self.n_y and self.y < self.f_y:
            move_coor[1] += 1
        else:
            pass

        return move_coor

    def move(self):
        others = self.check()

        self.safety_move()

        move_coor = self.normal_move()

        for other_x, other_y in others:
            if [other_x, other_y] == move_coor:
                print("(%d, %d) ; (%d, %d)" % (other_x, other_y, move_coor[0], move_coor[1]))

                # this is where I code what the AI does is there ARE other guys next to it
                # or even other obstacles

                #del self.closest_nibbles[0]
                self.safety_move()
                self.move_r()
                
                break

        else:
            self.x = move_coor[0]
            self.y = move_coor[1]
            print("(%d, %d) ; (%d, %d)" % (other_x, other_y, move_coor[0], move_coor[1]))
        
        

        self.eat_nibble()
        

        self.field[self.x][self.y] = self.id

    def move_r(self):
        lst = [1, 0, -1]
        self.field[self.x][self.y] = 0
        tmp = np.random.choice(lst)
        if tmp == -1:
            if self.x + tmp < 0:
                self.x += 1
            else:
                self.x -= 1
        elif tmp == 1:
            if self.x + tmp > self.f_x-1:
                self.x -= 1
            else:
                self.x += 1
        else:
            pass
                
        tmp = np.random.choice(lst)
        if tmp == -1:
            if self.y + tmp < 0:
                self.y += 1
            else:
                self.y -= 1
        elif tmp == 1:
            if self.y + tmp > self.f_y-1:
                self.y -= 1
            else:
                self.y += 1
        else:
            pass
        
        self.field[self.x][self.y] = self.id
        
    def check(self):
        self.closest_nibbles = euclid(self.x, self.y, self.Field.nibbles)
        self.n_x, self.n_y = self.closest_nibbles[0][1]
        print("(%d, %d)" % (self.n_x, self.n_y), end=":   ")

        if self.x == 1:
            ls_x = [0, 1]
        elif self.x >= self.f_x-1:
            ls_x = [-1, 0]
        else:
            ls_x = [-1, 0, 1]

        if self.y == 1:
            ls_y = [0, 1]
        elif self.y >= self.f_y-1:
            ls_y = [-1, 0]
        else:
            ls_y = [-1, 0, 1]

        
        obj = [(self.x+x, self.y+y) \
        for x in ls_x for y in ls_y \
        if 0 < self.field[self.x+x][self.y+y] < 1]
        if obj == []: obj = [(self.x, self.y)]
        print("In viscinity: %s" % str(obj), end=":   \n")
        return obj


    #########





    # FOR AI





    #########

    def fitness_eval(self):
        self.y = int(self.y)
        try: 
            if 0 < self.field[self.x][self.y] < 1 and self.field[self.x][self.y] != self.id:
                self.fitness -= 999.99

            elif self.is_at_nibble:
                self.fitness += 1

        except IndexError:
            self.fitness -= 999.99
            self.safety_move()


    def return_inputs(self):
        positions = [
                        (-1,1), (0,1), (1,1),
                        (-1,0), (0,0), (1,0),
                        (-1,-1), (0,-1), (1,-1)
                    ]
        positions_on_field = [(self.x+x, self.y+y) for x,y in positions]
        ids_of_positions = [0,0,0,0,0,0,0,0,0]
        for i in range(len(positions_on_field)):
            if positions_on_field[i][0] >= DIMENSION_SIZE or positions_on_field[i][1] >= DIMENSION_SIZE: 
                ids_of_positions[i] = -100.0
            
            else:
                ids_of_positions[i] = self.field[positions_on_field[i][0]][positions_on_field[i][1]]


        #ids_of_positions = [self.field[x][y] for x,y in positions_on_field]

        return ids_of_positions

    def move_AI(self, args):
        """
           0       0       0

           0       1       0        one_hot_vector is args parameter

           0       0       0
        
         (-1,1)  (0,1)   (1,1)

         (-1,0)  (0,0)   (1,0)      input differences from the centre

        (-1,-1)  (0,-1)  (1,-1)  
        

        """

        positions = [
                        (-1,1), (0,1), (1,1),
                        (-1,0), (0,0), (1,0),
                        (-1,-1), (0,-1), (1,-1)
                    ]

        #print(args)
        #position_x, position_y = list(filter(lambda x: x[1], zip(positions, args)))[0]
        position_x, position_y = max(enumerate(args), key= lambda x: x[0])

        position_on_field = (self.x + position_x, self.y + position_y)

        self.total_time += EPOCH_DELAY

        self.field[self.x][self.y] = 0
        self.x, self.y = position_on_field

        self.fitness_eval()
        self.eat_nibble()

        self.field[self.x][self.y] = self.id

            




        
if __name__ == '__main__':
    x = Field(DIMENSION_SIZE, DIMENSION_SIZE, nibbles = 100)
    creatures = np.array([Creature(x) for i in range(CREATURE_POPULATION)])
    system('clear')
    print("Start? [Y]/N ")
    if popen('read -n 1 y; echo $y').read()[0] not in ('N', 'n'):
        while True:
            #print('\033[0;0H%s' % str(x))
            print(x)
            system('clear')
            for k in creatures:
                k.move()
            time.sleep(EPOCH_DELAY)
            x.produce()


