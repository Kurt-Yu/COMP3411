class Coordinate:
    def __init__(self, x, y):
        self._x = x
        self._y = y
        self._visited = False
    
    @property
    def x(self):
        return self._x

    @property
    def y(self):
        return self._y

    @property
    def visited(self):
        return self._visited

    @visited.setter
    def visited(self, v):
        self._visited = v