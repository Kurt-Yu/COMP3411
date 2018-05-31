# base code provided by https://gist.github.com/jamiees2/5531924
## my comments are with two hashtags
## this code will get two points of interest and return the action

class Node:
    def __init__(self, value, point):
        self.value = value
        self.point = point
        self.parent = None
        self.H = 0
        self.G = 0

    def move_cost(self, other):
        return 0 if self.value == '.' else 1

def children(point, grid):
    
    x, y = point.point    ## x,y is the point of the agent
    ## x = x + 80
    ## y = y + 80
    min_coord = 0
    max_coord = len(grid[0])-1
    ## if and elif statement so algorithm does not produce a path for the agent outside the hashmap
    if min_coord < x < max_coord and min_coord < y < max_coord:
        links = [grid[d[0]][d[1]] for d in [(x-1, y),(x,y - 1),(x,y + 1),(x+1,y)]]
    elif y == min_coord and x == max_coord:
        links = [grid[d[0]][d[1]] for d in [(x-1,1),(x,y + 1)]]
    elif y == max_coord and x == min_coord:
        links = [grid[d[0]][d[1]] for d in [(x+1, y),(x,y - 1)]]
    elif y == min_coord and x == min_coord:
        links = [grid[d[0]][d[1]] for d in [(x+1, y),(x,y + 1)]]
    elif y == max_coord and x == max_coord:
        links = [grid[d[0]][d[1]] for d in [(x-1, y),(x,y - 1)]]
    elif y == max_coord and min_coord < x < max_coord:
        links = [grid[d[0]][d[1]] for d in [(x,y - 1),(x+1,y),(x-1,y)]]
    elif x == max_coord and min_coord < y < max_coord:
        links = [grid[d[0]][d[1]] for d in [(x,y - 1),(x-1, y),(x,y+1)]]
    elif y == min_coord and min_coord < x < max_coord:
        links = [grid[d[0]][d[1]] for d in [(x-1,y),(x+1, y),(x,y+1)]]
    else:
        links = [grid[d[0]][d[1]] for d in [(x, y-1),(x+1, y),(x,y+1)]]
    return [link for link in links if link.value != '*' and link.value != '~' and link.value != '-']

def manhattan(point,point2):
    return abs(point.point[0] - point2.point[0]) + abs(point.point[1]-point2.point[0])

def aStar(start, goal, grid):
    #The open and closed sets
    openset = set()
    closedset = set()
    #Current point is the starting point
    current = start
    #Add the starting point to the open set
    openset.add(current)
    #While the open set is not empty
    while openset:
        # Find the item in the open set with the lowest G + H score
        current = min(openset, key=lambda o:o.G + o.H)
        # If it is the item we want, retrace the path and return it
        if current == goal:
            path = []
            while current.parent:
                path.append(current)
                current = current.parent
            path.append(current)
            return path[::-1]
        #Remove the item from the open set
        openset.remove(current)
        #Add it to the closed set
        closedset.add(current)
        #Loop through the node's children/siblings
        for node in children(current,grid):
            #If it is already in the closed set, skip it
            if node in closedset:
                continue
            #Otherwise if it is already in the open set
            if node in openset:
                #Check if we beat the G score 
                new_g = current.G + current.move_cost(node)
                if node.G > new_g:
                    #If so, update the node to have a new parent
                    node.G = new_g
                    node.parent = current
            else:
                #If it isn't in the open set, calculate the G and H score for the node
                node.G = current.G + current.move_cost(node)
                node.H = manhattan(node, goal)
                #Set the parent to our current item
                node.parent = current
                #Add it to the set
                openset.add(node)
    #Throw an exception if there is no path
    raise ValueError('No Path Found')

def next_move(agent,tool,grid):
    #Convert all the points to instances of Node
    for x in range(len(grid)):
        for y in range(len(grid[x])):
            grid[x][y] = Node(grid[x][y],(x,y))
    ## Get the manhattan path between agent and useful tool or obstacle
    path = aStar(grid[agent[0]][agent[1]],grid[tool[0]][tool[1]],grid)
    #Output the path
    path_coordinates = []
    print(len(path) - 1)
    for node in path:
        x, y = node.point
        path_coordinates.append((x,y))
    return path_coordinates


# function to return the action of agent
def rotate(path_coordinates, grid):
    target_state = list(grid[agent_x][agent_y].value)
    for i in range(0, len(path_coordinates)-1):
        if path_coordinates[i+1][0] < path_coordinates[i][0]:
            target_state.append('^')
        elif path_coordinates[i+1][0] > path_coordinates[i][0]:
            target_state.append('v')
        elif path_coordinates[i+1][1] > path_coordinates[i][1]:
            target_state.append('>')
        else:
            target_state.append('<')
    return target_state

mapping_table = {('^', '>'): ('r'), ('^', 'v'): ('r', 'r'), ('^', '<'): ('l'), ('>', '^'): ('l'), ('>', 'v'): ('r'), ('>', '<'): ('r', 'r'),
('v', '>'): ('l'), ('v', '^'): ('r', 'r'), ('v', '<'): ('l'), ('<', '^'): ('r'), ('<', 'v'): ('l'), ('<', '>'): ('r', 'r')}


def action_to_take(target_state):
    action = []
    target_state = rotate(path_coordinates, grid)
    for i in range(0, len(target_state)-1):
        try:
            action.extend(mapping_table[str(target_state[i]),str(target_state[i+1])] + 'f')
        except KeyError:
            action.extend('f')
    return action
    

# append a list of action for agent to enact upon
# path between two coordinates if going via water

## location of the agent
agent_x, agent_y = 0, 0

## location of the useful tool/obstacle
axe_x, axe_y = 2,1

## size of the grid
## need to change to 160 and 160 
x,y = 2,2
 
#grid = hashmap
grid = [['^',' ', 'x'],
        ['*','*', 'x'],
        ['*',' ', 'x']]

path_coordinates = next_move((agent_x, agent_y),(axe_x, axe_y), grid)
print(path_coordinates)
print(rotate(path_coordinates, grid))
print(action_to_take(rotate(path_coordinates, grid)))


