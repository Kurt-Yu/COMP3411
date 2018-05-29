#!/usr/bin/python3
# ^^ note the python directive on the first line
# COMP 9414 agent initiation file 
# requires the host is running before the agent
# designed for python 3.6
# typical initiation would be (file in working directory, port = 31415)
#        python3 agent.py -p 31415
# created by Leo Hoare
# with slight modifications by Alan Blair

import sys
import socket

# declaring visible grid to agent
view = [['' for _ in range(5)] for _ in range(5)]

inventory = {'a':0, 'k':0, 'o':0, '$':0, 'r':0}

pickable = ['a', 'k', 'o', '$']

def move(view):
    if view[1][2] = ' ':
        view[2][2], view[1][2] = view[1][2], view[2][2]
        action.append('f')
    elif view[1][2] in pickable:
        inventory[view[1][2]] += 1
        view[2][2], view[1][2] = ' ', view[2][2]
    elif view[2][3] == ' ' or view[2][3] in pickable: 
        action.append('r')
    elif view[2][1] == ' ' or view[2][1] in pickable: 
        action.append('l')
    elif view[1][2] == 'T':
        if inventory['a'] >= 1:
            action.append('c') 
            inventory['r'] += 1
    elif view[1][2] == '-':
        if inventory['k'] >= 1:
            action.append('u')
    else: 
        action.append('r', 'r')
return action 



class Agent:
    def __init__(self):
        self.inventory = {'a':0, 'k':0, 'o':0, '$':0, 'r':0}

        self.axe_location = []
        self.key_location = []
        self.stepping_stone = []
        self.space_location = []
        self.water_location = []

        self.gold_location = None
        self.is_gold_found = False
        self.agent_x = 0
        self.agent_y = 0

        self.direction = '^'           # Always consider the agent direction is '^

        self.hashmap = {}              # Initialize the hashmap
        for i in range(-80, 81):
            for j in range(-80, 81):
                self.hashmap[(i, j)] = '?'
        self.hashmap[(0, 0)] = '^'
        
    def rotate(self, view, time):                 # rotate 2d list clockwise
        for i in range(time):
            temp = zip(*view[::-1])               # return a list of tuples
            view = [list(elem) for elem in temp]  # convert list of tuples to list of lists
        return view

    def get_front_tail(self):
        if self.direction == '^':
            return self.hashmap[(self.agent_x - 1, self.agent_y)]
        elif self.direction == '>':
            return self.hashmap[(self.agent_x, self.agent_y + 1)]
        elif self.direction == 'v':
            return self.hashmap[(self.agent_x + 1, self.agent_y)]
        else:
            return self.hashmap[(self.agent_x, self.agent_y - 1)]

    def update_from_view(self, view):
        # Rotate the view based on which direction the agent is facing
        if self.direction = '>':        
            view = self.rotate(view, 1)
        if self.direction = 'v':
            view = self.rotate(view, 2)
        if self.direction = '<':
            view = self.rotate(view, 3)

        # Iterate through the view and update the internal map
        for i in range(5):
            for j in range(5):
                x = self.agent_x - (2 - i)
                y = self.agent_y + (j - 2)
                self.hashmap[(x, y)] = view[i][j]
                if i == 2 and j == 2:
                    self.hashmap[(x, y)] = self.direction

                if view[i][j] == 'a' and (x, y) not in self.axe_location:
                    self.axe_location.append((x, y))
                if view[i][j] == 'k' and (x, y) not in self.key_location:
                    self.key_location.append((x, y))
                if view[i][j] == 'o' and (x, y) not in self.stepping_stone:
                    self.stepping_stone.append((x, y))
                # if view[i][j] == ' ' and (x, y) not in self.space_location:
                #     self.space_location.append((x, y))
                if view[i][j] == '~' and (x, y) not in self.water_location:
                    self.water_location.append((x, y))
                if view[i][j] == '$' and self.is_gold_found == False:
                    self.gold_location = (x, y)
                    self.is_gold_found = True

    def update_from_move(self, move):
        move = move.upper()          # convert move to upper case
        if move == 'L':
            if self.direction == '^':
                self.direction = '<'
            elif self.direction == '>':
                self.direction = '^'
            elif self.direction == 'v':
                self.direction = '>'
            else:
                self.direction = 'v'
        
        if move == 'R:
            if self.direction == '^':
                self.direction = '>'
            elif self.direction == '>':
                self.direction = 'v'
            elif self.direction == 'v':
                self.direction = '<'
            else:
                self.direction = '^'

        if move == 'F':
            thing = self.get_front_tail()
            if thing == '-' or thing == 'T' or thing == '*':  # if it's obstacles, do nothing
                return
            if thing == ' ':                                  # if it's space, move to this space
                
            if thing in pickable:
                inventory[thing] += 1
            










first_time = True

# function to take get action from AI or user
def get_action(view):
    ## REPLACE THIS WITH AI CODE TO CHOOSE ACTION ##
    if first_time:
        hashmap[()]
    

    # input loop to take input from user (only returns if this is valid)
    while 1:
        inp = input("Enter Action(s): ")
        inp.strip()
        final_string = ''
        for char in inp:
            if char in ['f','l','r','c','u','b','F','L','R','C','U','B']:
                final_string += char
                if final_string:
                     return final_string[0]

# helper function to print the grid
def print_grid(view):
    print('+-----+')
    for ln in view:
        print("|"+str(ln[0])+str(ln[1])+str(ln[2])+str(ln[3])+str(ln[4])+"|")
    print('+-----+')

if __name__ == "__main__":

    # checks for correct amount of arguments 
    if len(sys.argv) != 3:
        print("Usage Python3 "+sys.argv[0]+" -p port \n")
        sys.exit(1)

    port = int(sys.argv[2])

    # checking for valid port number
    if not 1025 <= port <= 65535:
        print('Incorrect port number')
        sys.exit()

    # creates TCP socket
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
         # tries to connect to host
         # requires host is running before agent
         sock.connect(('localhost',port))
    except (ConnectionRefusedError):
         print('Connection refused, check host is running')
         sys.exit()

    # navigates through grid with input stream of data
    i=0
    j=0
    while 1:
        data=sock.recv(100)
        if not data:
            exit()
        for ch in data:
            if (i==2 and j==2):
                view[i][j] = '^'
                view[i][j+1] = chr(ch)
                j+=1 
            else:
                view[i][j] = chr(ch)
            j+=1
            if j>4:
                j=0
                i=(i+1)%5
        if j==0 and i==0:
            print_grid(view) # COMMENT THIS OUT ON SUBMISSION
            action = get_action(view) # gets new actions
            sock.send(action.encode('utf-8'))

    sock.close()
