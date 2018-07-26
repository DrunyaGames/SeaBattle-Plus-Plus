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
        self.shoots = 0

    def shoot(self, *_):
        self.shoots += 1


class SpecialShip:
    def __init__(self, x, y, direction, field):
        self.field = field
        self.x = x
        self.y = y
        self.direction = direction
        self.shoots = 0

    def shoot(self, *_):
        self.shoots += 1


class Hospital(SpecialShip):
    name = 'hospital'

    def place(self):
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
        self.field.add_obj_to_cells(cells, self)

    def shoot(self, *_):
        super().shoot()
        self.field.player.game.change_turn()


class TShip(SpecialShip):
    name = 'tship'

    def place(self):
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

        self.field.add_obj_to_cells(cells, self)
