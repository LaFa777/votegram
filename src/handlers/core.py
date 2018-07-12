from telegram.ext import (
    Dispatcher,
)


class Handler:

    def __init__(self, dispatcher):
            self.dispatcher = dispatcher
            self.bind_handlers()

    def bind_handlers(self):
        raise NotImplementedError


class BuilderHandler(Handler):

    @classmethod
    def get_description(cls):
        """TODO: посчитать максимально комфортную длину описания
        """
        raise NotImplementedError
