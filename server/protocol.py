from easy_tcp.server import ServerFactory, protocol
from easy_tcp.models import Message
from config import PORT
from models import User
from errors import *
from game import Game

server = ServerFactory()


def auth_required(func):
    def wrapper(*args, **kwargs):
        if protocol.user:
            return func(*args, **kwargs)
        raise AuthError

    return wrapper


def check_turn(func):
    def wrapper(*args, **kwargs):
        # if True:
        #     return func(*args, **kwargs)
        if protocol.user and protocol.user.player \
                and protocol.user.player.id == game.turn and game.started:
            return func(*args, **kwargs)
        raise AuthError

    return wrapper


@server.on_close()
def on_close(_):
    protocol.connected = 0
    if not protocol.user:
        return
    protocol.user.leave_channel()
    if protocol.user.player:
        protocol.user.player.leave()


@server.handle('auth')
def auth(name: str, password: str) -> User:
    if password == 'test':
        user = User(name, protocol.copy())
        protocol.user = user
        protocol.send(Message('auth_ok', user.dump()))
        return user
    raise BadLogin


@auth_required
@server.handle('join')
def join():
    if game.started:
        raise GameError
    protocol.user.player = game.add_new_player(protocol.user)
    return protocol.send(Message('join_ok', {
        'self': protocol.user.player.dump(),
        'enemy': game.players[not protocol.user.player.id].dump() if
        len(game.players) > 1 else None,
        'turn': game.turn
    }))


@auth_required
@server.handle('place_ship')
def place(**kwargs):
    if not protocol.user.player:
        raise GameError
    protocol.user.player.place_ship(**kwargs)


@auth_required
@server.handle('ready')
def ready():
    if not protocol.user.player:
        raise GameError
    protocol.user.player.ready()


@check_turn
@server.handle('shoot')
def shoot(coords: list):
    protocol.user.player.shoot(coords)


@server.handle('random_place')
def random_place():
    protocol.user.player.random_place()


if __name__ == '__main__':
    game = Game()
    server.run(port=PORT)
