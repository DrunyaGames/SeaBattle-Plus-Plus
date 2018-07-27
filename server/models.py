import logging


class User:
    def __init__(self, name, protocol):
        self.name = name
        self.player = None
        self.proto = protocol
        self.channel = None

    def send(self, message):
        if not self.proto.connected:
            return
        self.proto.send(message)

    def leave_channel(self):
        if self.channel:
            self.channel.remove(self)

    def dump(self):
        return {
            'name': self.name,
            'player': self.player.dump() if self.player else None
        }


class Channel(set):

    def __init__(self, name, *args):
        super().__init__(*args)

        self.name = name
        self.log = logging.getLogger('<Channel %s>' % self.name)

    def shout(self, message):
        self.log.debug('Shout %s' % message.dump())
        for proto in self:
            proto.send(message, _log=False)

    def remove(self, element):
        element.channel = None
        super().remove(element)

    def add(self, element):
        element.channel = self
        super().add(element)
