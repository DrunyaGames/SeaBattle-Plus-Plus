from threading import Thread
import socket
import time
import json

offline = False


class Client(Thread):
    address = ('localhost', 8957)
    buffer_size = 8000

    delimiter = b'\r\n'

    def __init__(self):
        super().__init__()

        self.sock = None
        self.make_socket()

        self.handlers = {}
        self.error_handlers = {}

        if not offline:
            self.start()

    def make_socket(self):
        try:
            self.sock = socket.create_connection(self.address)
        except ConnectionRefusedError:
            self.reconnect()

    def reconnect(self):
        print('Reconnecting in 5 second')
        if self.sock:
            self.sock.close()
        time.sleep(5)
        self.make_socket()

    def send(self, message_type, data):

        if not self.sock:
            self.make_socket()

        try:
            self.sock.sendall(json.dumps({'type': message_type, 'data': data}).encode('utf-8') + self.delimiter)
        except ConnectionAbortedError:
            self.reconnect()

    def _recv(self):
        if not self.sock:
            self.make_socket()
        try:
            temp = self.sock.recv(self.buffer_size)
            if not temp:
                raise ConnectionAbortedError
            return temp
        except ConnectionAbortedError:
            self.reconnect()
            return

    def handle(self, event):
        def decorator(func):
            def wrapper(data):
                return func(**data)

            self.handlers[event] = wrapper
            return wrapper

        return decorator

    def error_handle(self, code):
        def decorator(func):
            def wrapper(data):
                return func(**data)

            self.error_handlers[code] = wrapper
            return wrapper

        return decorator

    def _recv_handle(self, message):
        if not message:
            return
        message = json.loads(message)
        message_type = message['type']

        if message_type == 'error':
            func = self.error_handlers.get(message['data']['code'])
        else:
            func = self.handlers.get(message_type)

        if func:
            func(message['data'])

    def run(self):
        while True:
            recv = self._recv()
            if recv:
                msgs = recv.strip(self.delimiter).split(self.delimiter)
                for msg in msgs:
                    self._recv_handle(msg)
