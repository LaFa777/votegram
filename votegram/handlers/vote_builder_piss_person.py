from ..handlers import (
    VoteBuilderTimerConversationHandler,
)


class VoteBuilderPissPersonConversationHandler(Handler):
    """Собирает голосование против нехорошего пользователя

    Этапы:
    1. выбор времени истечения
    2. ввод имени пользователя
    """

    def __init__(self,
                 dispatcher):

        self._timer_handler = VoteBuilderTimerConversationHandler()

        super().__init__(dispatcher)
