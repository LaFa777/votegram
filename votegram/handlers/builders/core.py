from telegram_addons import (
    ComponentHandler,
)


class VoteBuilder(ComponentHandler):

    def description(self):
        """Возвращает описание голосования
        """
        raise NotImplementedError
