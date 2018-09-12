from ...handlers import (
    Handler,
    ConversationHandler,
    CallbackDataBuilderV1,
    CallbackDataParserV1,
)

from ..modules import VoteConversationTimerHandler


class VoteBuilderPissHandler(ConversationHandler):
    """Собирает голосование против нехорошего пользователя

    Этапы:
    1. выбор времени истечения
    2. ввод имени пользователя

    TODO:
        1. Работает только в чате тет-а-тет
        2. Сделать упрощенную версию для чатов (аля /piss @user)
    """

    def __init__(self,
                 dispatcher):
        self._query_builder = CallbackDataBuilderV1()
        self._query_builder.set_salt(self.__class__.__name__)

        self._query_parser = CallbackDataParserV1()
        self._query_parser.set_salt(self.__class__.__name__)

        self._timer_handler = VoteConversationTimerHandler(
            dispatcher=dispatcher,
            query_builder=self._query_builder,
            query_parser=self._query_parser,
        )

        super().__init__(dispatcher)

    def bind_handlers(self, dispatcher):
        self._timer_handler.add_done_callback(self.timer_done)

    def start(self, bot, update):
        self._timer_handler.start(bot, update)

    def timer_done(self, bot, update, data):
        query = update.callback_query
        bot.send_message(chat_id=query.message.chat_id,
                         text="Вы выбрали время {}".format(data))
