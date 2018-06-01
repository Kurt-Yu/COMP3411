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

pickable = ['a', 'k', 'o', '$', ' ']

mapping_table = {(0, 1, '^'): ['r', 'f'], (0, 1, '>'): ['f', '>'], (0, 1, 'v'): ['l', 'f'], (0, 1, '<'): ['l', 'l', 'f'], 
                 (0, -1, '^'): ['l', 'f'], (0, -1, '>'): ['l', 'l', 'f'], (0, -1, 'v'): ['r', 'f'], (0, -1, '<'): ['f'],
                 (1, 0, '^'): ['l', 'l', 'f'], (1, 0, '>'): ['r', 'f'], (1, 0, 'v'): ['f'], (1, 0, '<'): ['l', 'f'],
                 (-1, 0, '^'): ['f'], (-1, 0, '>'): ['l', 'f'], (-1, 0, 'v'): ['l', 'l', 'f'], (-1, 0, '<'): ['r', 'f']}

get_direction = {(0, 1): '>', (0, -1): '<', (1, 0): 'v', (-1, 0): '^'}

class Node:
    def __init__(self, value, point):
        self.value = value
        self.point = point
        self.parent = None
        self.visited = False
        self.H = 0
        self.G = 0

    def move_cost(self, other):
        return 0 if self.value == '.' else 1
  
class Agent:
    def __init__(self):
        self.inventory = {'a':False, 'k':False, '$':False, 'r':False, 'o':0}

        self.axe_location = []
        self.key_location = []
        self.stepping_stone = []
        self.space_location = []
        self.water_location = []
        self.tree_location = []
        self.gold_location = []

        self.unvisited = []     # use to stored all the walkable but unvisited cells
        
        self.agent_x = 0
        self.agent_y = 0

        self.direction = '^'                  # Always consider the agent direction is '^'  

        self.grid = [[ '?' for i in range(160)] for j in range(160)]   # create a 2d list that store all the Node objects
        for x in range(len(self.grid)):          
            for y in range(len(self.grid[x])):
                self.grid[x][y] = Node(self.grid[x][y], (x, y))

        self.pending_move = []                # list to store the pending moves
        
    def rotate(self, view, time):                 # rotate 2d list clockwise
        for _ in range(time):
            temp = zip(*view[::-1])               # return a list of tuples
            view = [list(elem) for elem in temp]  # convert list of tuples to list of lists
        return view

    def can_move(self):
        node = self.get_front_tail()
        if node.value in pickable:
            return True
        return False

    def get_front_tail(self):                     # get the grid in front the agent
        if self.direction == '^':
            x = self.agent_x - 1
            y = self.agent_y
        elif self.direction == '>':
            x = self.agent_x
            y = self.agent_y + 1
        elif self.direction == 'v':
            x = self.agent_x + 1
            y = self.agent_y
        else:
            x = self.agent_x
            y = self.agent_y - 1
        return self.grid[x][y]

    def update_from_view(self, view):
        # Rotate the view based on which direction the agent is facing
        if self.direction == '>':        
            view = self.rotate(view, 1)
        if self.direction == 'v':
            view = self.rotate(view, 2)
        if self.direction == '<':
            view = self.rotate(view, 3)

        self.grid[self.agent_x][self.agent_y].visited = True

        # Iterate through the view and update the internal map
        for i in range(5):
            for j in range(5):
                x = self.agent_x - (2 - i)
                y = self.agent_y + (j - 2)
                self.grid[x][y].value = view[i][j]

                # stored all adjacent cells which can actually walk through
                if view[i][j] in pickable:
                    if (i == 1 and j == 2) or (i == 2 and j == 1) or (i == 2 and j == 3) or (i == 3 and j == 2):
                        if (x, y) not in self.unvisited and self.grid[x][y].visited == False:
                            self.unvisited.append((x, y))

                if i == 2 and j == 2:
                    self.grid[x][y].value = self.direction

                if view[i][j] == 'a' and (x, y) not in self.axe_location:
                    self.axe_location.append((x, y))
                if view[i][j] == 'k' and (x, y) not in self.key_location:
                    self.key_location.append((x, y))
                if view[i][j] == 'o' and (x, y) not in self.stepping_stone:
                    self.stepping_stone.append((x, y))
                if view[i][j] == ' ' and (x, y) not in self.space_location:
                    self.space_location.append((x, y))
                if view[i][j] == '~' and (x, y) not in self.water_location:
                    self.water_location.append((x, y))
                if view[i][j] == 'T' and (x, y) not in self.tree_location:
                    self.tree_location.append((x, y)) 
                if view[i][j] == '$' and (x, y) not in self.gold_location:
                    self.gold_location.append((x, y))

    
    def children(self, node):
        x, y = node.point    
        
        result = []
        for r, c in [(x - 1, y), (x, y + 1), (x + 1, y), (x, y - 1)]:
            if r >= 0 and r < len(self.grid[0]) and c >= 0 and c < len(self.grid) and self.grid[r][c].value in pickable:
                result.append(self.grid[r][c])
        return result

    def manhattan(self, a, b):
        return abs(a.point[0] - b.point[0]) + abs(a.point[1] - b.point[0])

    # this A star algorithm is adapted from https://gist.github.com/jamiees2/5531924
    # with slightly modify to server our purpose
    def aStar(self, start, goal): # each grid element is a node object
        openset = set()           # The open set
        closedset = set()         # The closed set

        current = start           # Current point is the starting point
        openset.add(current)      # Add the starting point to the open set
        
        while openset:            # While the open set is not empty
            current = min(openset, key=lambda o:o.G + o.H)

            if current.point == goal.point:
                path = []
                while current.parent:
                    path.append(current.point)
                    current = current.parent
                path.append(current.point)
                return path[::-1]

            openset.remove(current)     # Remove the item from the open set
            closedset.add(current)      # Add it to the closed set

            for node in self.children(current):
                if node in closedset:   # If it is already in the closed set, skip it
                    continue
                
                if node in openset:     # Otherwise if it is already in the open set
                    new_g = current.G + current.move_cost(node)
                    if node.G > new_g:
                        node.G = new_g
                        node.parent = current
                else:
                    node.G = current.G + current.move_cost(node)
                    node.H = self.manhattan(node, goal)
                    node.parent = current   # Set the parent to our current item
                    openset.add(node)       # Add it to the set
        return None                         # return None if no path is found

    def update_from_move(self, move):
        front = self.get_front_tail()   # get the grid in front
        x, y = front.point
        move = move.upper()                   # Convert to upper case
         
        if move == 'L':
            if self.direction == '^':
                self.direction = '<'
            elif self.direction == '>':
                self.direction = '^'
            elif self.direction == 'v':
                self.direction = '>'
            else:
                self.direction = 'v'

        if move == 'R':
            if self.direction == '^':
                self.direction = '>'
            elif self.direction == '>':
                self.direction = 'v'
            elif self.direction == 'v':
                self.direction = '<'
            else:
                self.direction = '^'

        if move == 'F':
            if front in ['*', '-', 'T', ' ']:      # Do nothing
                return

            self.agent_x, self.agent_y = x, y   # update the agent's location
            if front == 'a':
                self.axe_location.remove((x, y))
                self.inventory['a'] = True
            if front == 'k':
                self.key_location.remove((x, y))
                self.inventory['k'] = True
            if front == '$':
                self.gold_location.remove((x, y))
                self.inventory['$'] = True
            if front == 'o':
                self.stepping_stone.remove((x, y))
                self.inventory['o'] += 1
            if front == '~':
                if self.inventory['o'] <= 0 and self.inventory['r']:
                    self.inventory['r'] == False
                if self.inventory['o'] >= 1:
                    self.inventory['o'] -= 1
                    self.water_location.remove((x, y))

        if move == 'C' and front== 'T':
            self.inventory['r'] = True

    def take_action(self):
        while len(self.unvisited) != 0:
            start = (self.agent_x, self.agent_y)
            end = self.unvisited.pop()
            path = self.aStar(self.grid[start[0]][start[1]], self.grid[end[0]][end[1]])
            if not path:
                break
            self.pending_move += self.path_to_actions(path)

    # convert a list of coordinate tuples to a list of actions
    def path_to_actions(self, path):
        actions = []
        for i in range(len(path) - 1):
            abs_x = path[i + 1][0] - path[i][0]
            abs_y = path[i + 1][1] - path[i][1]
            actions += mapping_table[(abs_x, abs_y, self.direction)]
            self.direction = get_direction[(abs_x, abs_y)]
        return actions
    
    def print_list(self, input_list):
        print('\n'.join(map(''.join, input_list)))

agent = Agent()

# function to take get action from AI or user
def get_action(view):
    agent.update_from_view(view)
    agent.take_action()
    action = agent.pending_move.pop(0)
    agent.update_from_move(action)
    return action 
    # # input loop to take input from user (only returns if this is valid)
    # while 1:
    #     inp = input("Enter Action(s): ")
    #     inp.strip()
    #     final_string = ''
    #     for char in inp:
    #         if char in ['f','l','r','c','u','b','F','L','R','C','U','B']:
    #             final_string += char
    #             if final_string:
    #                  return final_string[0]

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
