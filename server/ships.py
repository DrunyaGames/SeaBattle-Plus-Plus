from errors import *


class BaseShip:
    name = '%s deck'

    def __init__(self, ship_len, x, y, direction, field):
        self.len = ship_len
        self.field = field
        self.x = x
        self.y = y
        self.direction = direction
        self.name = self.name % self.len

        self.shoots = []
        self.shoots_count = 0
        self.is_dead = False

    @property
    def cells(self):
        x, y = self.x, self.y
        if not self.direction and y - self.len + 1 >= 0:
            cells = [self.field[x, i + 1] for i in range(y - self.len, y)]

        elif self.direction == 1:
            cells = [self.field[i, y] for i in range(x, x + self.len)]

        elif self.direction == 2:
            cells = [self.field[x, i] for i in range(y, y + self.len)]

        elif self.direction == 3 and x - self.len + 1 >= 0:
            cells = [self.field[i + 1, y] for i in range(x - self.len, x)]
        else:
            raise BadFieldCoords
        return cells

    def place(self):
        self.field.add_obj_to_cells(self.cells, self)

    def shoot(self, x, y):
        self.shoots_count += 1
        if (x, y) not in self.shoots:
            self.shoots.append((x, y))
        if len(self.shoots) >= self.len:
            self.is_dead = True


class SpecialShip:
    def __init__(self, x, y, direction, field):
        self.field = field
        self.x = x
        self.y = y
        self.direction = direction

        self.n = 0
        self.shoots = []
        self.shoots_count = 0
        self.is_dead = False

    def shoot(self, x, y):
        self.shoots_count += 1
        if (x, y) not in self.shoots:
            self.shoots.append((x, y))
        if len(self.shoots) >= self.n:
            self.is_dead = True


class Hospital(SpecialShip):
    name = 'hospital'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.is_dead = True

    @property
    def cells(self):
        x, y = self.x, self.y
        if y - 1 < 0 or x - 1 < 0:
            raise BadFieldCoords
        cells = [
            self.field[x, y],
            self.field[x, y + 1],
            self.field[x, y - 1],
            self.field[x + 1, y],
            self.field[x - 1, y]
        ]
        return cells

    def place(self):
        self.field.add_obj_to_cells(self.cells, self)

    def shoot(self, x, y):
        super().shoot(x, y)
        self.field.player.missed_turns += 1


class TShip(SpecialShip):
    name = 'trawler'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.n = 4

    @property
    def cells(self):
        x, y = self.x, self.y
        if self.direction in [0, 2]:
            if x - 1 < 0 or y - 1 < 0 and not self.direction:
                raise BadFieldCoords

            cells = [
                self.field[x, y],
                self.field[x + 1, y],
                self.field[x - 1, y],
                self.field[x, y - 1] if not self.direction else self.field[x, y + 1]
            ]
        else:
            if y - 1 < 0 or self.direction == 3 and x - 1 < 0:
                raise BadFieldCoords

            cells = [
                self.field[x, y],
                self.field[x, y + 1],
                self.field[x, y - 1],
                self.field[x + 1, y] if self.direction == 1 else self.field[x - 1, y]
            ]
        return cells

    def place(self):
        self.field.add_obj_to_cells(self.cells, self)
