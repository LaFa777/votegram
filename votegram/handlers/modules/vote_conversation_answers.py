import copy

from ...handlers import (
    ModuleHandler,
)

from telegram.ext import (
    ConversationHandler,
    CommandHandler,
    MessageHandler,
    CommandHandler,
    Filters,
)

from ...telegram_utils import (
    Message,
    ConversationHandlerWrapper,
)

from telegram import (
    Update,
)

ANSWER_INPUT = range(1)


class Render:
    @staticmethod
    def form_start():
        return Message("Введи ответ или введи /done для окончания ввода.")

    @staticmethod
    def form_add_answer():
        return Message("Ви таки успешно добавили ответ.\n/done для конца")


class VoteConvesationAnswersHandler(ModuleHandler):
    """Запрашивает у пользователя варианты ответа. В data возвращает массив
    строк введенных пользователем (1 на каждое сообщение).

    Todo:
      добавить возможность удаления ответов?
      ограничение по добавленным ответам
    """

    def __init__(self,
                 dispatcher,
                 query_builder,
                 query_parser):
        self._query_builder = copy.copy(query_builder)
        self._query_parser = copy.copy(query_parser)
        self._conv_handler = None
        self._render = Render()

        super().__init__(dispatcher)

    def bind_handlers(self, dispatcher):
        self._conv_handler = ConversationHandlerWrapper(
            entry_points=[],
            states={
                ANSWER_INPUT: [MessageHandler(Filters.text, self.answers_add)],
            },
            fallbacks=[
                CommandHandler('done', self.answers_done),
            ]
        )
        dispatcher.add_handler(self._conv_handler)

    def start(self, bot, update):
        # инициируем вход(entry_points) в ConversationHandler
        self._conv_handler.set_state(update, ANSWER_INPUT)
        self.answers_start(bot, update)

    def answers_start(self, bot, update):
        """Показывает сообщение о вводе или /done для отмены
        """
        tg_message = Render().form_start().to_telegram(self._query_builder)
        chat_id = None
        if update.message:
            chat_id = update.message.chat_id
        elif update.callback_query:
            chat_id = update.callback_query.message.chat_id
        else:
            # Выбрасывать ошибка
            pass
        bot.send_message(chat_id=chat_id,
                         **tg_message)

        return ANSWER_INPUT

    def answers_add(self, bot, update):
        tg_message = Render().form_add_answer().to_telegram(self._query_builder)
        bot.send_message(chat_id=update.message.chat_id,
                         **tg_message)

    def answers_done(self, bot, update):
        # parser = self._query_parser
        # query = update.callback_query
        # answers = parser.get_data(query.data)
        answers = ["За", "глу", "шка"]

        # передаем данные слушателю
        self.notify(bot, update, answers)
