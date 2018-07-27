from client import Client
from pygame.locals import *
from string import ascii_lowercase
import pygame
import time

client = Client()


class NoneObject:
    color = (150, 150, 150)

    def __init__(self, cell):
        self.cell = cell
        self.screen = cell.screen
        self.rect = Rect(cell.rect.x + 1, cell.rect.y + 1, Game.k - 1, Game.m - 1)

    def draw(self):
        pygame.draw.rect(self.screen, self.color, self.rect)

    def delete(self):
        self.cell.object = self.cell.last_object


class TargetObject(NoneObject):
    color = (37, 78, 161)


class MarkNoneObject(NoneObject):
    color = (120, 120, 120)


class TempShip(NoneObject):
    color = (119, 209, 149)


class BaseShip(NoneObject):
    color = (122, 4, 4)


class OurShip(NoneObject):
    color = (27, 107, 60)


class Mark:
    k = 3

    def __init__(self, cell, n):
        self.cell = cell
        self.screen = cell.screen
        self.font = pygame.font.Font(None, 25)
        self.n = str(n)

    def draw(self):
        self.screen.blit(self.font.render(self.n, True, (0, 0, 0)),
                         (self.cell.rect.center[0] - self.k, self.cell.rect.center[1] - self.k))


class Ship:

    def __init__(self, x, y, direction, field, ship_len=4):
        self.len = ship_len
        self.type = str(ship_len)
        self.field = field
        self.x = x
        self.y = y
        self.direction = direction

    def change_coords(self, x, y):
        self.x, self.y = x, y

    def change_direction(self):
        self.direction += 1
        if self.direction > 3:
            self.direction = 0

    def place(self, img=False):
        # self.field.del_temp()
        try:
            x, y = self.x, self.y
            if not self.direction and y - self.len + 1 >= 0:
                cells = [self.field[i + 1][x] for i in range(y - self.len, y)]

            elif self.direction == 1:
                cells = [self.field[y][i] for i in range(x, x + self.len)]

            elif self.direction == 2:
                cells = [self.field[i][x] for i in range(y, y + self.len)]

            elif self.direction == 3 and x - self.len >= 0:
                cells = [self.field[y][i + 1] for i in range(x - self.len, x)]
            else:
                raise IndexError

            for cell in cells:
                if cell.object and not isinstance(cell.object, TempShip):
                    return

            if img:
                self.field.draw(cells, TempShip)
            else:
                self.field.add_obj_to_cells(cells, BaseShip)
        except IndexError:
            return False
        return True


class Hospital(Ship):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.type = 'h'

    def place(self, img=False):
        try:
            x, y = self.x, self.y

            if y - 1 < 0 or x - 1 < 0:
                return

            cells = [
                self.field[y][x],
                self.field[y + 1][x],
                self.field[y - 1][x],
                self.field[y][x + 1],
                self.field[y][x - 1]
            ]

            for cell in cells:
                if cell.object and not isinstance(cell.object, TempShip):
                    return

            if img:
                self.field.draw(cells, TempShip)
            else:
                self.field.add_obj_to_cells(cells, BaseShip)
        except IndexError:
            return False
        return True


class TShip(Ship):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.type = 't'

    def place(self, img=False):
        try:
            x, y = self.x, self.y
            if self.direction in [0, 2]:
                if x - 1 < 0 or y - 1 < 0 and not self.direction:
                    return

                cells = [
                    self.field[y][x],
                    self.field[y][x + 1],
                    self.field[y][x - 1],
                    self.field[y - 1][x] if not self.direction else self.field[y + 1][x]
                ]
            else:
                if y - 1 < 0 or self.direction == 3 and x - 1 < 0:
                    return

                cells = [
                    self.field[y][x],
                    self.field[y + 1][x],
                    self.field[y - 1][x],
                    self.field[y][x + 1] if self.direction == 1 else self.field[y][x - 1]
                ]
            for cell in cells:
                if cell.object and not isinstance(cell.object, TempShip):
                    return

            if img:
                self.field.draw(cells, TempShip)
            else:
                self.field.add_obj_to_cells(cells, BaseShip)
        except IndexError:
            return
        return True


class Cell:
    def __init__(self, x, y, field, obj=None):
        self.x, self.y = x, y
        self.n = field.n
        k, m = Game.k, Game.m
        real_x = k // 2 + x * k - k // 2 + (Game.win_field_width + Game.win_interval) * (self.n - 1)
        real_y = m // 2 + y * m - m // 2
        self.rect = pygame.Rect(real_x, real_y, k, m)

        self.field = field
        self.screen = field.screen
        self.object = obj
        self.last_object = obj

        self.mark_object = None
        self.instance = 0

    def change_obj(self, obj):
        self.object = obj
        if isinstance(obj, NoneObject):
            self.last_object = obj

    def delete(self):
        self.object = self.last_object
        self.last_object = None

    def on_press(self):
        if self in self.field.targets:
            self.field.targets.remove(self)
            self.object = self.last_object
        elif len(self.field.targets) < 3:
            self.field.targets.append(self)
            self.last_object = self.object
            self.object = TargetObject(self)

    def draw(self):
        pygame.draw.rect(self.screen, (0, 0, 0), self.rect, 1)
        if self.mark_object:
            self.mark_object.draw()
        if self.object:
            self.object.draw()

    def mark(self):
        if not self.instance:
            self.last_object = self.object
            self.object = MarkNoneObject(self)
        elif self.instance == 1:
            self.object = BaseShip(self)
        else:
            self.object = self.last_object
        self.instance += 1
        if self.instance > 2:
            self.instance = 0

    def __bool__(self):
        return bool(self.object)


class History(list):
    ind = 20
    size = 25
    len = 19

    def __init__(self, _game):
        self.game = _game
        self.screen = _game.screen

        self.output_rect = pygame.Rect(Game.win_field_width * 2 + Game.win_interval + 40, 0,
                                       Game.win_additional_width - 50,
                                       Game.win_field_height)
        self.font = pygame.font.Font(None, self.size)
        super().__init__()

    def add(self, *messages):
        for message in messages:
            self.append(message)

    def append(self, obj):
        super().append(obj)
        if len(self) > 19:
            self.pop(0)

    def draw(self):
        pygame.draw.rect(self.screen, (100, 100, 100), self.output_rect, 2)
        for i, message in enumerate(self):
            self.screen.blit(self.font.render(
                str(message[1]) + ':' + '   ' + message[0], True, (0, 0, 0)), (
                self.output_rect.x + 10,
                self.output_rect.y + self.ind * (i + 1)
            ))


class Field(list, pygame.sprite.Sprite):
    size = 10

    def __init__(self, _game, n=1):
        pygame.sprite.Sprite.__init__(self)
        list.__init__(self)
        self.game = _game
        self.screen = _game.screen
        self.n = n
        self.mark_n = 0
        self.targets = []
        self.to_del = []

        for y in range(self.size):
            self.append([Cell(x, y, self) for x in range(self.size)])

        self.cells = []
        for row in self:
            self.cells += row

    def del_temp(self):
        for obj in self.to_del:
            obj.delete()
        self.to_del.clear()

    def shoot(self):
        # if self.game.player.id != self.game.turn:
        #     return
        if len(self.targets) < 3:
            return
        client.send('shoot', {'coords': [(target.x, target.y) for target in self.targets]})
        for target in self.targets.copy():
            target.on_press()

    def update(self):

        for row in self:
            for cell in row:
                cell.draw()

        k, m = Game.k, Game.m

        for i, letter in enumerate(ascii_lowercase[:10]):
            x = k + k * i - k // 2 - 3 + (Game.win_field_width + Game.win_interval) * (self.n - 1)
            self.screen.blit(self.game.font.render(letter, True, (0, 0, 0)),
                             (x, Game.win_field_height + 8))

        for i in range(10):
            y = m + m * i - m // 2 - 8
            self.screen.blit(self.game.font.render(str(i), True, (0, 0, 0)),
                             (Game.win_field_width + 8 +
                              (Game.win_field_width + Game.win_interval) * (self.n - 1), y))

        if not game.player:
            return
        if game.turn is None:
            turn = 'Никто'

        elif game.turn == game.player.id:
            turn = 'Вы'
        else:
            turn = 'Противник'

        self.screen.blit(self.game.font.render('Сейчас ходит: %s' % turn, True, (0, 0, 0)),
                         ((Game.win_field_width + Game.win_interval) * 2, Game.display[1] - 40))

    @staticmethod
    def add_obj_to_cells(cells, obj):
        for cell in cells:
            cell.change_obj(obj(cell))

    def draw(self, cells, obj):
        for cell in cells:
            self.to_del.append(cell)
            cell.object = obj(cell)


class Player:
    def __init__(self, name, player_id):
        self.name = name
        self.id = player_id


class Game:
    win_field_width = 400
    win_field_height = 400
    win_interval = 50
    win_additional_width = 400
    win_additional_height = 50

    field_width = 10
    field_height = 10

    k, m = win_field_width // field_width, win_field_height // field_height

    display = (win_field_width * 2 + win_interval + win_additional_width, win_field_height + win_additional_height)
    background_color = (240, 240, 240)
    fps = 20

    def __init__(self):
        pygame.init()
        pygame.font.init()
        self.font = pygame.font.Font(None, 25)
        self.screen = pygame.display.set_mode(self.display)
        pygame.display.set_caption("SeaBattle++")
        self.bg = pygame.Surface(self.display)
        self.bg.fill(self.background_color)

        self.history = History(self)
        self.field = Field(self, n=2)
        self.enemy_field = Field(self)
        self.main_loop = True

        self.shoot_button = pygame.Rect(
            20, self.win_field_height + self.win_additional_height // 2, 50, 20
        )

        self.player = None
        self.enemy = None

        self.available_ships = {
            Ship(0, 0, 0, self.field, 4): 1,
            Ship(0, 0, 0, self.field, 3): 2,
            Ship(0, 0, 0, self.field, 2): 3,
            Ship(0, 0, 0, self.field, 1): 4,
            Hospital(0, 0, 0, self.field): 1,
            TShip(0, 0, 0, self.field): 1
        }
        self.current_ship = None
        self.select_next_ship()

        self.turn = 0

    def add_player(self, player):
        self.player = player

    def add_enemy(self, player):
        self.enemy = player

    def select_next_ship(self):
        ships = list(self.available_ships.keys())
        if ships:
            ship = ships[0]
            self.available_ships[ship] -= 1
            if self.available_ships[ship] <= 0:
                self.available_ships.pop(ship)
            self.current_ship = ship
        else:
            self.current_ship = None
            client.send('ready', {})

    def change_turn(self):
        self.turn = not self.turn

    def run(self):
        while self.main_loop:

            for event in pygame.event.get():
                if event.type == QUIT:
                    exit()
                if event.type == MOUSEBUTTONDOWN:
                    mouse_pos = event.pos
                    if event.button == 1:
                        # noinspection PyArgumentList
                        if self.shoot_button.collidepoint(mouse_pos):
                            self.enemy_field.shoot()
                            continue

                    for cell in self.enemy_field.cells:
                        if cell.rect.collidepoint(mouse_pos):
                            if event.button == 1:
                                cell.on_press()
                            elif event.button == 3:
                                cell.mark()
                            break

                    if self.current_ship:
                        for cell in self.field.cells:
                            if cell.rect.collidepoint(mouse_pos):
                                if event.button == 1 and self.current_ship.place():
                                    client.send('place_ship', {
                                        'x': self.current_ship.x,
                                        'y': self.current_ship.y,
                                        'direction': self.current_ship.direction,
                                        'ship_type': self.current_ship.type
                                    })
                                    self.select_next_ship()
                                elif event.button == 3:
                                    self.field.del_temp()
                                    self.current_ship.change_direction()
                                    self.current_ship.place(img=True)
                                break

                if event.type == MOUSEMOTION:
                    self.field.del_temp()
                    mouse_pos = event.pos

                    if self.current_ship:
                        for cell in self.field.cells:
                            if cell.rect.collidepoint(mouse_pos):
                                self.current_ship.change_coords(cell.x, cell.y)
                                self.current_ship.place(img=True)
                                break

            self.screen.blit(self.bg, (0, 0))
            time.sleep(1 / self.fps)
            self.field.update()
            self.enemy_field.update()
            self.history.draw()

            pygame.draw.rect(self.screen, (0, 0, 0), self.shoot_button)

            pygame.display.update()


def coord_to_coord(x, y, add=0):
    return x * Game.k + add, \
           y * Game.m + add


@client.handle('auth_ok')
def auth(**_):
    client.send('join', {})


@client.handle('join_ok')
def join(self, enemy, turn):
    game.turn = turn
    game.add_player(Player(**self))
    if enemy:
        game.add_enemy(Player(**enemy))


@client.handle('player_shoot')
def player_shoot(player, result, coords, turn):
    game.turn = turn
    if player['player_id'] == game.player.id:
        if not result:
            for coord in coords:
                cell = game.enemy_field[coord[1]][coord[0]]
                cell.change_obj(NoneObject(cell))
        else:
            game.history.append((', '.join(list(map(str, result))),
                                 game.enemy_field.mark_n))
            for coord in coords:
                cell = game.enemy_field[coord[1]][coord[0]]
                cell.mark_object = Mark(cell, game.enemy_field.mark_n)
            game.enemy_field.mark_n += 1
    else:
        for coord in coords:
            cell = game.field[coord[1]][coord[0]]
            if not cell and not isinstance(cell.object, NoneObject):
                cell.object = NoneObject(cell)
            else:
                cell.object = OurShip(cell)


if __name__ == '__main__':
    game = Game()
    time.sleep(1)

    client.send('auth', {'name': 'admin', 'password': 'test'})
    print('Started')
    game.run()
