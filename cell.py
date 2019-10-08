class Cell:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.up = None
        self.down = None
        self.left = None
        self.right = None

    def __eq__(self, other):
        return self.x == other.x and self.y == other.y
