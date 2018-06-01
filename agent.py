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
from astar import *
from queue import PriorityQueue

# declaring visible grid to agent
view = [['' for _ in range(5)] for _ in range(5)]

pickable = ['a', 'k', 'o', '$', ' ']
  
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

        self.hashmap = {}                     # Initialize the hashmap
        for i in range(-79, 80):              # size 159 * 159 
            for j in range(-79, 80):  
                self.hashmap[(i, j)] = ['?', False]  # Initialize the hashmap to unkown value, represent by '?'    
        self.hashmap[(0, 0)] = ['^', True]           # always consider the agent is facing up      

        self.pending_move = []                # list to store the pending moves
        
    def rotate(self, view, time):                 # rotate 2d list clockwise
        for _ in range(time):
            temp = zip(*view[::-1])               # return a list of tuples
            view = [list(elem) for elem in temp]  # convert list of tuples to list of lists
        return view

    def can_move(self):
        x, y, front = self.get_front_tail()
        if front[0] in [' ', 'k', 'a']:
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
        return x, y, self.hashmap[(x, y)]

    def update_from_view(self, view):
        # Rotate the view based on which direction the agent is facing
        if self.direction == '>':        
            view = self.rotate(view, 1)
        if self.direction == 'v':
            view = self.rotate(view, 2)
        if self.direction == '<':
            view = self.rotate(view, 3)

        self.hashmap[(self.agent_x, self.agent_y)][1] = True

        # Iterate through the view and update the internal map
        for i in range(5):
            for j in range(5):
                x = self.agent_x - (2 - i)
                y = self.agent_y + (j - 2)
                self.hashmap[(x, y)][0] = view[i][j]

                # stored all adjacent cells which can actually walk through
                if view[i][j] in pickable:
                    if (i == 1 and j == 2) or (i == 2 and j == 1) or (i == 2 and j == 3) or (i == 3 and j == 2):
                        if (x, y) not in self.unvisited and self.hashmap[(x, y)][1] == False:
                            self.unvisited.append((x, y))

                if i == 2 and j == 2:
                    self.hashmap[(x, y)][0] = self.direction

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

    def update_from_move(self, move):
        x, y, front = self.get_front_tail()   # get the grid in front
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

            self.agent_x, self.agent_y = x, y      # update the agent's location
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
            path, cost = self.a_star_search(self.convert_hashmap_to_list(), start, end)


    # The A* star algorithm, base code come from https://dbader.org/blog/priority-queues-in-python
    # with slightly modify to server our porpuse
    def heuristic(self, a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    def neighbors(self, graph, point):
        result = []
        x, y = point
        if x - 1 >= 0 and graph[x - 1][y] == ' ':
            result.append((x - 1, y))
        if y - 1 >= 0 and graph[x][y - 1] == ' ':
            result.append((x, y - 1))
        if y + 1 < len(graph[0]) and graph[x][y - 1] == ' ':
            result.append((x, y + 1))
        if x + 1 < len(graph) and graph[x + 1][y] == ' ':
            result.append((x + 1, y))
        return result

    def a_star_search(self, graph, start, goal):
        frontier = PriorityQueue()
        frontier.put(start, 0)
        came_from = {}
        cost_so_far = {}
        came_from[start] = None
        cost_so_far[start] = 0
        
        while not frontier.empty():
            current = frontier.get()
            
            if current == goal:
                break
            
            for next in self.neighbors(graph, current):
                new_cost = cost_so_far[current] + 1
                if next not in cost_so_far or new_cost < cost_so_far[next]:
                    cost_so_far[next] = new_cost
                    priority = new_cost + self.heuristic(goal, next)
                    frontier.put(next, priority)
                    came_from[next] = current
        
        return came_from, cost_so_far



    # def astar(self, grid, start, end, direction):


    def convert_hashmap_to_list(self):
        result = [[ ' ' for i in range(160)] for j in range(160)]
        for i in range(-79, 80):
            for j in range(-79, 80):
                result[i + 79][j + 79] = self.hashmap[(i, j)][0]
        return result
    
    def print_list(self, input_list):
        print('\n'.join(map(''.join, input_list)))

    # This function is adapted from https://stackoverflow.com/questions/398299/looping-in-a-spiral
    # with slightly modify to server our purporse
    def spiral_traversal(self):
        x = y = 0
        dx, dy = 0, -1
        for _ in range(159 ** 2):
            if (-159 / 2 < x <= 159 / 2) and (-159 / 2 < y <= 159 / 2):
                print (x, y)
                # DO STUFF...
            if x == y or (x < 0 and x == -y) or (x > 0 and x == 1 - y):
                dx, dy = -dy, dx
            x, y = x+dx, y+dy

    # This function is adpated from: http://inventwithpython.com/blogstatic/floodfill/recursivefloodfill.py
    # with slight modify to serve our porpuse
    # parameters: 
    #    game_map is the 2d list that represent the whole map
    #    x & y: the coordinates of starting point
    #    old_value & new_value: some character that we would like to change
    # return:
    #   Modified game_map which agent can reach from start point to anywhere else
    def flood_fill(self, game_map, x, y, old_value, new_value, inventory):
        width = len(game_map)
        height = len(game_map[0])

        if old_value == None:
            old_value = game_map[x][y]

        if game_map[x][y] != old_value: # Base case. If the current x, y character is not the old_value, then do nothing.
            return

        game_map[x][y] = new_value      # Change the character at world[x][y] to newChar

        # Recursive calls. Make a recursive call as long as we are not on the
        # boundary (which would cause an Index Error.)
        if x > 0: # left
            self.flood_fill(game_map, x - 1, y, old_value, new_value, inventory)
        if y > 0: # up
            self.flood_fill(game_map, x, y - 1, old_value, new_value, inventory)
        if x < width - 1: # right
            self.flood_fill(game_map, x + 1, y, old_value, new_value, inventory)
        if y < height-1: # down
            self.flood_fill(game_map, x, y + 1, old_value, new_value, inventory)

agent = Agent()

# function to take get action from AI or user
def get_action(view):
    agent.update_from_view(view)
    action = agent.take_action()

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
