import time

EMPTY_SPACE_SYMBOLS = ' '
STARTING_POINT_SYMBOLS = '^'
OBSTACLE_SYMBOL = '~'
DIRS = [(-1, 0), (1, 0), (0, 1), (0, -1)]

class HamiltonSolver:
    def __init__(self, grid):
        self.grid = grid
        self.h = h = len(grid)
        self.w = w = len(grid[0])

        self.start = None
        self.legal = set()
        for r, row in enumerate(grid):
            for c, item in enumerate(row):
                if item in STARTING_POINT_SYMBOLS:
                    self.start = (r, c)
                elif item in EMPTY_SPACE_SYMBOLS:
                    self.legal.add((r, c))

    def format_solution(self, path):
        """Format a path as a string."""
        grid = [[OBSTACLE_SYMBOL] * self.w for _ in range(self.h)]
        for i, (r, c) in enumerate(path, start=1):
            grid[r][c] = i
        w = len(str(len(path) + 1)) + 1
        return '\n'.join(''.join(str(item).ljust(w) for item in row)
                         for row in grid)

    def solve(self):
        """Generate solutions as lists of coordinates."""
        target_path_len = len(self.legal) + 1
        paths = [[self.start]]
        while paths:
            path = paths.pop()
            if len(path) == target_path_len:
                yield path
            r, c = path[-1]
            for dr, dc in DIRS:
                new_coord = r + dr, c + dc
                if new_coord in self.legal and new_coord not in path:
                    paths.append(path + [new_coord])

PUZZLE_GRID = '''
~~~~~~~~~~~~~~~~~~~~~~
~~~~~~~~~~~~~~~~~~~~~~
~~                  ~~
~~     ^            ~~
~~    ~~~           ~~
~~   ~~~~~          ~~
~~  ~~~~~~~         ~~
~~  ~~~~~~~~        ~~
~~   ~~~~~~~~       ~~
~~    ~~~~~~~~      ~~
~~     ~~~~~~~~     ~~
~~      ~~~~~~~~    ~~
~~       ~~~~~~~~   ~~
~~        ~~~~~~~~  ~~
~~         ~~~~~~~  ~~
~~          ~~~~~   ~~
~~           ~~~    ~~
~~            ~     ~~
~~                  ~~
~~~~~~~~~~~~~~~~~~~~~~
~~~~~~~~~~~~~~~~~~~~~~
'''.split('\n')[1:-1]

def main():
    start_time = time.time()
    n_solutions = 0
    puzzle = HamiltonSolver(PUZZLE_GRID)
    for solution in puzzle.solve():
        if n_solutions == 0:
            print(puzzle.format_solution(solution))
            print("First solution found in {} s"
                  .format(time.time() - start_time))
        n_solutions += 1
    print("{} solution{} found in {} s"
          .format(n_solutions, '' if n_solutions == 1 else 's',
                  time.time() - start_time))

if __name__ == '__main__':
    main()

