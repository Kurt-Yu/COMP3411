from queue import PriorityQueue

def heuristic(a, b):
    return abs(a[0] - b[0]) + abs(a[1] - b[1])

def neighbors(graph, point):
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


def a_star_search(graph, start, goal):
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
        
        for next in neighbors(graph, current):
            new_cost = cost_so_far[current] + heuristic(current, next)
            if next not in cost_so_far or new_cost < cost_so_far[next]:
                cost_so_far[next] = new_cost
                priority = new_cost + heuristic(goal, next)
                frontier.put(next, priority)
                came_from[next] = current
    
    return came_from, cost_so_far


grid = [[' ',' ', ' '],
        ['*','*', ' '],
        ['*',' ', ' ']]

path, cost = a_star_search(grid, (0, 0), (2, 1))
print(path)

