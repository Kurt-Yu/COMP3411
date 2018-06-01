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


pickable = ['a', 'k', 'o', '$', ' ']

mapping_table = {(0, 1, '^'): ['r', 'f'], (0, 1, '>'): ['f'], (0, 1, 'v'): ['l', 'f'], (0, 1, '<'): ['l', 'l', 'f'], 
                 (0, -1, '^'): ['l', 'f'], (0, -1, '>'): ['l', 'l', 'f'], (0, -1, 'v'): ['r', 'f'], (0, -1, '<'): ['f'],
                 (1, 0, '^'): ['l', 'l', 'f'], (1, 0, '>'): ['r', 'f'], (1, 0, 'v'): ['f'], (1, 0, '<'): ['l', 'f'],
                 (-1, 0, '^'): ['f'], (-1, 0, '>'): ['l', 'f'], (-1, 0, 'v'): ['l', 'l', 'f'], (-1, 0, '<'): ['r', 'f']}

get_direction = {(0, 1): '>', (0, -1): '<', (1, 0): 'v', (-1, 0): '^'}

d = '^'

def children(node, grid):
    x, y = node.point    
    
    result = []
    for r, c in [(x - 1, y), (x, y + 1), (x + 1, y), (x, y - 1)]:
        if r >= 0 and r < len(grid[0]) and c >= 0 and c < len(grid) and grid[r][c].value in pickable:
            result.append(grid[r][c])
    return result

def manhattan(a, b):
    return abs(a.point[0] - b.point[0]) + abs(a.point[1]-b.point[0])

def aStar(start, goal, grid): # each grid element is a node object
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

        for node in children(current, grid):
            if node in closedset:   # If it is already in the closed set, skip it
                continue
            
            if node in openset:     # Otherwise if it is already in the open set
                new_g = current.G + current.move_cost(node)
                if node.G > new_g:
                    node.G = new_g
                    node.parent = current
            else:
                node.G = current.G + current.move_cost(node)
                node.H = manhattan(node, goal)
                node.parent = current   # Set the parent to our current item
                openset.add(node)       # Add it to the set

    raise ValueError('NO Path Found')

def next_move(start, end, grid):        # each grid element is a value
    for x in range(len(grid)):          # Convert all the points to instances of Node
        for y in range(len(grid[x])):
            grid[x][y] = Node(grid[x][y], (x, y))

    path = aStar(grid[start[0]][start[1]], grid[end[0]][end[1]], grid)
    return path

# # function to return the action of agent
# def rotate(path_coordinates, grid):
#     target_state = list(grid[agent_x][agent_y].value)
#     for i in range(0, len(path_coordinates)-1):
#         if path_coordinates[i+1][0] < path_coordinates[i][0]:
#             target_state.append('^')
#         elif path_coordinates[i+1][0] > path_coordinates[i][0]:
#             target_state.append('v')
#         elif path_coordinates[i+1][1] > path_coordinates[i][1]:
#             target_state.append('>')
#         else:
#             target_state.append('<')
#     return target_state

# mapping_table = {('^', '>'): ('r'), ('^', 'v'): ('r', 'r'), ('^', '<'): ('l'), ('>', '^'): ('l'), ('>', 'v'): ('r'), ('>', '<'): ('r', 'r'),
# ('v', '>'): ('l'), ('v', '^'): ('r', 'r'), ('v', '<'): ('l'), ('<', '^'): ('r'), ('<', 'v'): ('l'), ('<', '>'): ('r', 'r')}


# def action_to_take(target_state):
#     action = []
#     for i in range(0, len(target_state)-1):
#         try:
#             action.extend(mapping_table[str(target_state[i]),str(target_state[i+1])] + 'f')
#         except KeyError:
#             action.extend('f')
#     return action

def path_to_actions(came_from):
    global d
    actions = []
    for i in range(len(came_from) - 1):
        abs_x = came_from[i + 1][0] - came_from[i][0]
        abs_y = came_from[i + 1][1] - came_from[i][1]
        actions += mapping_table[(abs_x, abs_y, d)]
        d = get_direction[(abs_x, abs_y)]

    return actions
    

# append a list of action for agent to enact upon
# path between two coordinates if going via water

## location of the agent
# agent_x, agent_y = 0, 0

## location of the useful tool/obstacle
# axe_x, axe_y = 2,1

## size of the grid
## need to change to 160 and 160 
# x,y = 2,2
 
#grid = hashmap
grid = [[' ', ' ', ' ', ' '],
        ['*', ' ', '*', ' '],
        ['*', ' ', ' ', ' '],
        [' ', ' ', ' ', ' ']]

path = next_move((0, 0), (1, 3), grid)
print(path)
print(path_to_actions(path))


