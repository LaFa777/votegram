from telegram.ext import (
    Dispatcher,
)


class Handler:

    def __init__(self, dispatcher, bind=True):
            self._dispatcher = dispatcher
            if bind:
                self.bind_handlers()

    def bind_handlers(self):
        raise NotImplementedError


class BuilderHandler(Handler):
    pass
