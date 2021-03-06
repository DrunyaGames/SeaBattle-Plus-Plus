from ships import *
from errors import *
from easy_tcp.models import Message
from models import Channel
import random


class Cell:

    def __init__(self, x, y, obj=None):
        if not (0 <= x < Field.size and 0 <= y < Field.size):
            raise IncorrectPlaceShip
        self.object = obj
        self.x = x
        self.y = y
        self.shoots = 0

    def shoot(self):
        self.shoots += 1
        if self.object:
            self.object.shoot(self.x, self.y)
            return self.object
        return None

    def __bool__(self):
        return bool(self.object)

    def __repr__(self):
        return '%s' % self.object.name[0] if self.object else ' '


class Row(list):

    def __getitem__(self, y):
        try:
            return super().__getitem__(y)
        except IndexError:
            raise BadFieldCoords


class Field(Row):
    size = 10

    def __init__(self, player):
        super().__init__()

        self.player = player
        for y in range(self.size):
            self.append(Row(Cell(x, y) for x in range(self.size)))

    def __getitem__(self, item):
        if isinstance(item, tuple):
            return super().__getitem__(item[1])[item[0]]
        return super().__getitem__(item)

    @staticmethod
    def add_obj_to_cells(cells, obj):
        for cell in cells:
            if cell.object:
                raise BadFieldCoords
        for cell in cells:
            cell.object = obj

    def __repr__(self):
        return '\n'.join(map(str, self))


class Player:

    def __init__(self, user, game, player_id):
        self.available_ships = {'4': 1, '3': 2, '2': 3, '1': 4, 't': 1, 'h': 1}

        self.name = user.name
        self.id = player_id

        self.user = user
        self.game = game
        self.field = Field(self)
        self.targets = []

        self.ships = []

        self.is_ready = False
        self.missed_turns = 0
        self.turns = 0

    def place_ship(self, ship_type, x, y, direction):

        if not self.available_ships.get(ship_type):
            return

        if ship_type not in self.available_ships or self.available_ships[ship_type] < 0:
            raise GameError

        if ship_type not in ['t', 'h']:
            ship = BaseShip(int(ship_type), x, y, direction, self.field)
        elif ship_type == 'h':
            ship = Hospital(x, y, direction, self.field)
        elif ship_type == 't':
            ship = TShip(x, y, direction, self.field)
        else:
            raise GameError
        ship.place()
        self.ships.append(ship)
        self.available_ships[ship_type] -= 1

    def shoot(self, coords):
        ind = not self.id if len(self.game.players) > 1 else 0
        cells = [self.game.players[ind].field[x, y] for x, y in coords]
        ships = [cell.shoot() for cell in cells]
        random.shuffle(ships)
        self.game.change_turn()
        data = {
            'turn': self.game.turn,
            'player': self.dump(),
            'coords': coords,
            'result': [(ship.name, ship.shoots_count) for ship in list(set(ships)) if ship]
        }
        self.game.channel.shout(Message('player_shoot', data))
        return data

    def random_place(self, count=20):
        for ship in self.available_ships:
            while self.available_ships[ship] > 0:
                while True:
                    try:
                        self.place_ship(ship, random.randint(0, 9), random.randint(0, 9), random.randint(0, 3))
                        break
                    except BaseError:
                        pass
                count -= 1
                if count <= 0:
                    return

    def check_win(self):
        return all([ship.is_dead for ship in self.ships])

    def ready(self):
        self.is_ready = True
        self.game.start()

    def leave(self):
        self.game.players.remove(self)
        if not self.game.players:
            self.game.started = False

    def dump(self):
        return {
            'name': self.name,
            'player_id': self.id,
        }


class Game:
    one_player = True

    def __init__(self):
        self.players = []
        self.history = []

        self.channel = Channel('game')

        self.turn = random.randint(0, 1)
        self.started = False

    def add_new_player(self, user):
        if len(self.players) >= 2:
            raise GameError
        player = Player(user, self, len(self.players))
        self.channel.shout(Message('new_player_connected', player.dump()))
        self.players.append(player)
        if user.proto:
            self.channel.add(user.proto)
        return player

    def start(self):
        if len(self.players) == 2 and \
                all([player.is_ready for player in self.players]):
            self.started = True

    def change_turn(self):
        player = self.players[self.turn] if len(self.players) > 1 else self.players[0]
        player.turns += 1
        if player.missed_turns:
            self.turn = not self.turn
            player.missed_turns -= 1
            return self.change_turn()
        self.turn = not self.turn
