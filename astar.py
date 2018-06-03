# base code provided by https://gist.github.com/jamiees2/5531924
## my comments are with two hashtags
## this code will get two points of interest and return the action

class Astar:
    def __init__(self, grid):
        self.grid = grid

    def children(self, node):
        x, y = node.point    
        
        result = []
        for r, c in [(x - 1, y), (x, y + 1), (x + 1, y), (x, y - 1)]:
            if r >= 0 and r < len(self.grid[0]) and c >= 0 and c < len(self.grid) and self.grid[r][c].value in [' ', 'a', 'k', 'o', '$']:
                result.append(self.grid[r][c])
        return result

    def manhattan(self, a, b):
        return abs(a.point[0] - b.point[0]) + abs(a.point[1]-b.point[0])

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
        raise ValueError('No Path Found')

