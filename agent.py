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
import copy

# declaring visible grid to agent
view = [['' for _ in range(5)] for _ in range(5)]

pickable = ['a', 'k', 'o', '$', ' ']

mapping_table = {(0, 1, '^'): ['r', 'f'], (0, 1, '>'): ['f'], (0, 1, 'v'): ['l', 'f'], (0, 1, '<'): ['l', 'l', 'f'], 
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
        return 0 if self.value == ' ' else 1
  
class Agent:
    def __init__(self):
        self.inventory = {'a':False, 'k':False, '$':False, 'r':False, 'o':0}

        self.axe_location = []
        self.key_location = []
        self.stepping_stone = []
        self.water_location = []
        self.tree_location = []
        self.gold_location = []
        self.door_location = []

        self.unvisited = []                  # use to stored all the walkable but unvisited cells
        self.on_water = False

        self.agent_x = 80
        self.agent_y = 80
        self.initial_x = 80
        self.initial_y = 80
        self.temp_x = 0
        self.temp_y = 0

        self.direction = '^'                  # Always consider the agent direction is '^'  

        self.grid = [[ '?' for i in range(160)] for j in range(160)]   # create a 2d list that store all the Node objects
        for x in range(len(self.grid)):          
            for y in range(len(self.grid[x])):
                self.grid[x][y] = Node(self.grid[x][y], (x, y))

        self.pending_move = []                # list to store the pending moves

    # Helper function 
    def rotate(self, view, time):                 # rotate 2d list clockwise
        for _ in range(time):
            temp = zip(*view[::-1])               # return a list of tuples
            view = [list(elem) for elem in temp]  # convert list of tuples to list of lists
        return view
    
    def print_list(self, input_list):
        print('\n'.join(map(''.join, input_list)))

    # the the cell in front of agent
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

#######################################################################################
########## Line 95 to Line 170, Update the self.grid list from view and from move 
#######################################################################################

    def update_from_view(self, view, on_water):
        # Rotate the view based on which direction the agent is facing
        if self.direction == '>':        
            view = self.rotate(view, 1)
        if self.direction == 'v':
            view = self.rotate(view, 2)
        if self.direction == '<':
            view = self.rotate(view, 3)

        self.grid[self.agent_x][self.agent_y].visited = True
        self.grid[self.agent_x][self.agent_y].value = self.direction

        # Iterate through the view and update the internal map
        for i in range(5):
            for j in range(5):
                x = self.agent_x - (2 - i)
                y = self.agent_y + (j - 2)
                self.grid[x][y].value = view[i][j]

                # stored all adjacent cells which can actually walk through
                if (i == 1 and j == 2) or (i == 2 and j == 1) or (i == 2 and j == 3) or (i == 3 and j == 2):
                    if (x, y) not in self.unvisited and self.grid[x][y].visited == False:
                        if view[i][j] in pickable and on_water == False:
                            self.unvisited.append((x, y))
                        if on_water:
                            if view[i][j] == '~':
                                self.unvisited.append((x, y))
                            if view[i][j] in pickable:
                                self.unvisited.insert(0, (x, y))

                if view[i][j] == 'a' and self.grid[x][y] not in self.axe_location:
                    self.axe_location.append(self.grid[x][y])
                if view[i][j] == 'k' and self.grid[x][y] not in self.key_location:
                    self.key_location.append(self.grid[x][y])
                if view[i][j] == '-' and self.grid[x][y] not in self.door_location:
                    self.door_location.append(self.grid[x][y])
                if view[i][j] == 'o' and self.grid[x][y] not in self.stepping_stone:
                    self.stepping_stone.append(self.grid[x][y])
                if view[i][j] == '~' and self.grid[x][y] not in self.water_location:
                    self.water_location.append(self.grid[x][y])
                if view[i][j] == 'T' and self.grid[x][y] not in self.tree_location:
                    self.tree_location.append(self.grid[x][y]) 
                if view[i][j] == '$' and self.grid[x][y] not in self.gold_location:
                    self.gold_location.append(self.grid[x][y])
        print('At this stage, the agent direction is: ' + self.direction)
        print("At this moment, the agent coordinate is: ({0}, {1})".format(self.agent_x, self.agent_y))
        print('The unvisited list is: {0}'.format(self.unvisited))
        print('The on_water variable is: {0}'.format(self.on_water))

    def update_inventory(self, x, y):
        if self.grid[x][y].value == 'a':
            if self.grid[x][y] in self.axe_location:
                self.axe_location.remove(self.grid[x][y])
            self.inventory['a'] = True
        if self.grid[x][y].value == 'k':
            if self.grid[x][y] in self.key_location:
                self.key_location.remove(self.grid[x][y])
            self.inventory['k'] = True
        if self.grid[x][y].value == 'o':
            if self.grid[x][y] in self.stepping_stone:
                self.stepping_stone.remove(self.grid[x][y])
            self.inventory['o'] += 1
        if self.grid[x][y].value == '$':
            if self.grid[x][y] in self.gold_location:
                self.gold_location.remove(self.grid[x][y])
            self.inventory['$'] = True
        if self.grid[x][y].value == 'T':
            if self.grid[x][y] in self.tree_location:
                self.tree_location.remove(self.grid[x][y])
            self.inventory['r'] = True


#######################################################################################
############       Line 176 to Line 237, A* algorithm     #############################
#######################################################################################
    def children(self, node, on_water, grid):
        x, y = node.point    

        result = []
        for r, c in [(x - 1, y), (x, y + 1), (x + 1, y), (x, y - 1)]:
            if r >= 0 and r < len(grid[0]) and c >= 0 and c < len(grid):
                if grid[r][c].value in pickable and on_water == False:
                    result.append(grid[r][c])
                if on_water and grid[r][c].value == '~':
                    result.append(grid[r][c])      
        return result

    def manhattan(self, a, b):
        return abs(a.point[0] - b.point[0]) + abs(a.point[1] - b.point[1])

    def clean_up(self, grid):
        for i in range(len(grid)):
            for j in range(len(grid[i])):
                grid[i][j].G = 0
                grid[i][j].H = 0
                grid[i][j].parent = None

    # this A star algorithm is adapted from https://gist.github.com/jamiees2/5531924
    # with slightly modify to server our purpose
    def aStar(self, start, goal, grid): # each grid element is a node object
        self.clean_up(grid)
        openset = set()           # The open set
        closedset = set()         # The closed set

        current = start           # Current point is the starting point
        openset.add(current)      # Add the starting point to the open set
        
        while openset:            # While the open set is not empty
            current = min(openset, key=lambda o:o.G + o.H)

            if current.point == goal.point:
                path = []
                while current.parent:
                    current.visited = True
                    path.append(current.point)
                    current = current.parent
                path.append(current.point)
                current.visited = True
                self.clean_up(grid)
                return path[::-1]

            openset.remove(current)     # Remove the item from the open set
            closedset.add(current)      # Add it to the closed set

            for node in self.children(current, self.on_water, grid):
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
        self.clean_up(grid)
        return None                     # return None if no path is found

    # Helper function, given a list of tools, return a part of them that can actual reach by agent
    def reachable_tools(self, tool_list):
        result = []
        for element in tool_list:
            x, y = element.point
            if self.grid[x - 1][y].visited or self.grid[x][y - 1].visited or self.grid[x][y + 1].visited or self.grid[x + 1][y].visited:
                result.append(element)
                # tool_list.remove(element)
        return result
    
    def near_the_tool(self, node, on_water, raft=False):
        x, y = node.point
        for i, j in [(x - 1, y), (x, y - 1), (x, y + 1), (x + 1, y)]:
            if on_water:
                if self.grid[i][j].value == '~':
                    return self.grid[i][j]
            if not on_water:
                if self.grid[i][j].value == ' ' and self.grid[i][j].visited:
                    return self.grid[i][j]



    # Flood Fill algorithm adpated from http://inventwithpython.com/blogstatic/floodfill/recursivefloodfill.py
    # with slightly modify to server our purpose

    def floodFill(self, world, x, y, oldChar, newChar):
        worldWidth = len(world)
        worldHeight = len(world[0])

        if oldChar == None:
            oldChar = world[x][y].value

        if world[x][y].value != oldChar:
            return

        world[x][y].value = newChar

        if x > 0: # left
            self.floodFill(world, x-1, y, oldChar, newChar)

        if y > 0: # up
            self.floodFill(world, x, y-1, oldChar, newChar)

        if x < worldWidth-1: # right
            self.floodFill(world, x+1, y, oldChar, newChar)

        if y < worldHeight-1: # down
            self.floodFill(world, x, y+1, oldChar, newChar)


    # if the self.unvisited list is not empty, means there are still some nodes that agent didn't go to.
    #pop the last element of the list out, if this node is adjecent to agent, then just call path_to_action function with the correct path
    # if this node is not adjecent to agent, do a A* search, return all the path coordinates that the agent need to follow, then call path_to_actions to get a series of moves    
    def take_action(self):
        if self.inventory['$']:
            path = self.aStar(self.grid[self.agent_x][self.agent_y], self.grid[80][80], self.grid)
            return self.path_to_actions(path)
        
        if len(self.unvisited) != 0:
            start = (self.agent_x, self.agent_y)
            end = self.unvisited.pop()
            if abs(start[0] - end[0]) + abs(start[1] - end[1]) == 1:
                return self.path_to_actions([start, end])
            
            path = self.aStar(self.grid[start[0]][start[1]], self.grid[end[0]][end[1]], self.grid)
            if not path and self.on_water:
                node = self.near_the_tool(self.grid[end[0]][end[1]], self.on_water)
                path = self.aStar(self.grid[self.agent_x][self.agent_y], node, self.grid)
                path.append(end)
                self.on_water = False
                self.inventory['r'] = False
                return self.path_to_actions(path)
            
            if not path and self.on_water == False:
                while True:
                    end = self.unvisited.pop()
                    path = self.aStar(self.grid[self.agent_x][self.agent_y], self.grid[end[0]][end[1]], self.grid)
                    if not path:
                        continue
                    return self.path_to_actions(path)
            return self.path_to_actions(path)

        # else when the self.unvisited list is empty
        # that means the agent has visit every node that it can reach
        # Then it should use tools to cut trees and unlock doors
        if self.inventory['a'] and self.inventory['r'] == False:
            reachable_tree = self.reachable_tools(self.tree_location)
            while len(reachable_tree) != 0:
                tree = reachable_tree.pop()
                node = self.near_the_tool(tree, self.on_water) 
                print(tree.point)
                print(node.point)
                print(self.agent_x, self.agent_y)
                print(self.on_water)
                path = self.aStar(self.grid[self.agent_x][self.agent_y], node, self.grid)
                path.append(tree.point)
                moves = self.path_to_actions(path)
                moves.insert(-1, 'c')
                if tree in self.tree_location:
                    self.tree_location.remove(tree)
                return moves

        if self.inventory['k']:
            reachable_door = self.reachable_tools(self.door_location)
            while len(reachable_door) != 0: 
                door = reachable_door.pop()

                node = None
                node = self.near_the_tool(door, self.on_water)
                # print('Node is {0}'.format(node.point))
                # print(door.point)
                # print(self.agent_x, self.agent_y)
                if not node:
                    node = self.near_the_tool(door, False)
                
                path = self.aStar(self.grid[self.agent_x][self.agent_y], node, self.grid)
                if not path:
                    if self.on_water == False:
                        self.temp_x, self.temp_y = self.agent_x, self.agent_y

                        nearest = None
                        distance = 160
                        for i in self.water_location:
                            t = abs(i.point[0] - self.agent_x) + abs(i.point[1] - self.agent_y)
                            if t < distance:
                                distance = t
                                nearest = i

                        act = None
                        if distance == 1:
                            act = self.path_to_actions([(self.agent_x, self.agent_y), nearest.point])
                        else:
                            nearest_land = self.near_the_tool(nearest, self.on_water)
                            p = self.aStar(self.grid[self.agent_x][self.agent_y], nearest_land, self.grid)
                            p.append(nearest.point)
                            act = self.path_to_actions(p)
                            self.on_water = True
                        print(self.grid[self.agent_x][self.agent_y].value)
                        if self.grid[self.agent_x][self.agent_y] == '~':
                            self.on_water = True
                        return act
                    else:
                        adjecent_water = None
                        print(self.agent_x, self.agent_y)
                        
                        for m, n in [(self.agent_x - 1, self.agent_y), (self.agent_x, self.agent_y - 1), (self.agent_x, self.agent_y + 1), (self.agent_x + 1, self.agent_y)]:
                            if m >= 0 and m < len(self.grid) and n >= 0 and n < len(self.grid[0]) and self.grid[m][n].value == '~':
                                adjecent_water = self.grid[m][n]
                                break
                        print(adjecent_water.value)
                        print(adjecent_water.point)
                        c = self.my_copy()
                        self.floodFill(c, self.temp_x, self.temp_y, ' ', '#')
                        self.floodFill(c, adjecent_water.point[0], adjecent_water.point[1], '~', ' ')
                        self.on_water = False
                        
                        print(self.agent_x, self.agent_y)
                        print(node.point)
                        print(c[81][95].value)
                        print(c[82][96].value)
                        path = self.aStar(c[self.agent_x][self.agent_y], node, c)
                        path.append(door.point)
                        moves = self.path_to_actions(path)
                        moves.insert(-1, 'u')
                        if door in self.door_location:
                            self.door_location.remove(door)
                        return moves

                path.append(door.point)
                moves = self.path_to_actions(path)
                moves.insert(-1, 'u')
                return moves
        
        # At this stage, the agent would already cut all the trees and unlock all the doors, depending on the inventory
        # Now, the agent must use raft or stepping stone to explore more
        if self.inventory['r'] and self.on_water == False:
            reachable_water = self.reachable_tools(self.water_location)
            water = reachable_water.pop()
            node = self.near_the_tool(water, self.on_water)
            path = self.aStar(self.grid[self.agent_x][self.agent_y], node, self.grid)
                    
            path.append(water.point)
            moves = self.path_to_actions(path)
            self.on_water = True
            return moves


    # convert a list of coordinate tuples to a list of actions
    def path_to_actions(self, path):
        actions = []
        for i in range(len(path) - 1):
            abs_x = path[i + 1][0] - path[i][0]
            abs_y = path[i + 1][1] - path[i][1]
            actions += mapping_table[(abs_x, abs_y, self.direction)]
            self.direction = get_direction[(abs_x, abs_y)]
            self.agent_x += abs_x
            self.agent_y += abs_y
            self.update_inventory(self.agent_x, self.agent_y)
            self.grid[self.agent_x][self.agent_y].visited = True
            if self.grid[self.agent_x][self.agent_y].value == '~':
                self.on_water = True
            if self.grid[self.agent_x][self.agent_y].value == ' ':
                self.on_water = False 
            if (self.agent_x, self.agent_y) in self.unvisited:
                self.unvisited.remove((self.agent_x, self.agent_y))
        print('After the moves, the agent coordinates is ({0} {1})'.format(self.agent_x, self.agent_y))
        print('The value stored at this place is: {0}'.format(self.grid[self.agent_x][self.agent_y].value))
        print('The inventory is: {0}'.format(self.inventory))
        return actions

    def my_copy(self):
        result = [['?' for _ in range(160)] for _ in range(160)]
        for i in range(len(self.grid)):
            for j in range(len(self.grid[i])):
                node = Node(self.grid[i][j].value, self.grid[i][j].point)
                result[i][j] = node
        return result


############################################################################################
######################## Above are the code for Node and Agent class #######################

agent = Agent()
actions = []

# function to take get action from AI or user
def get_action(view):

    global actions
    
    if len(actions) == 0:
        agent.update_from_view(view, agent.on_water)
        actions = agent.take_action()
        print('The action that supposed to take is: {0}'.format(actions) , '\n')
        return actions.pop(0)
    else:
        temp = actions.pop(0)
        print('The action that supposed to take is: {0}'.format(list(temp)), '\n')
        return temp

    # while 1:
    #     inp = input("Enter Action(s): ")
    #     # return actions.pop(0)
    #     return inp

    # while 1:
    #     inp = input("Enter Action(s): ")
    #     inp.strip()
    #     final_string = ''
    #     for char in inp:
    #         if char in ['f','l','r','c','u','b','F','L','R','C','U','B']:
    #             final_string += char
    #             if final_string:
    #                 agent.update_from_move(final_string[0])
    #                 return final_string[0]

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
