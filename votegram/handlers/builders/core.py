from ...handlers import Handler


class VoteBuilderHandler(Handler):
    def start(self, bot, update):
        """Выполняет шаги по сборке голосования
        """
        raise NotImplementedError
