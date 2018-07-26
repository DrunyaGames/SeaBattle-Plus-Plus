from easy_tcp.errors import BaseError


class GameError(BaseError):
    code = '200'
    message = 'Game Error'


class AuthError(BaseError):
    code = '100'
    message = 'Auth required'


class BadLogin(AuthError):
    code = '101'
    message = 'Incorrect login or password'


class IncorrectPlaceShip(GameError):
    code = '102'
    message = 'Wrong cords or direction'


class BadFieldCoords(GameError):
    code = '103'
    message = 'Coords out the field'
