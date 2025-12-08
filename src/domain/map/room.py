class Room:
    def __init__(self, left: int, top : int, width: int, height: int):
        self.left = left
        self.top = top
        self.width = width
        self.height = height
    @property
    def right(self):
        return self.left + self.width
    @property
    def bottom(self):
        return self.top + self.height
    @property
    def center(self):
        return self.left + self.width // 2, self.top + self.height // 2

    def door_right(self):
        y = self.top + self.height // 2
        x = self.right - 1
        return x, y

    def door_left(self):
        y = self.top + self.height // 2
        x = self.left
        return x, y

    def door_top(self):
        x = self.left + self.width // 2
        y = self.top
        return x, y

    def door_bottom(self):
        x = self.left + self.width // 2
        y = self.bottom - 1
        return x, y