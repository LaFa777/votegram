from telegram.ext import (
    CommandHandler,
    MessageHandler,
    Filters,
)

from ...handlers import (
    ModuleHandler,
)

from ...telegram_utils import (
    TextMessage,
    ConversationHandlerExt,
)

ANSWER_INPUT = range(1)


class Render:
    @staticmethod
    def form_start():
        return TextMessage("Введите свой варинт ответа\nОтправьте /done для окончания ввода.")

    @staticmethod
    def form_add_answer():
        return TextMessage("Ответ успешно добавлен.\nОтправьте /done для окончания ввода.")


class VoteConvesationAnswersHandler(ModuleHandler):
    """Запрашивает у пользователя варианты ответа. В data возвращает массив
    строк введенных пользователем (1 на каждое сообщение).

    Todo:
      добавить возможность удаления ответов?
      ограничение по количеству добавляемых ответов
    """

    def __init__(self, dispatcher, query_serializer):
        self._conv_handler = None
        self._render = Render()
        super().__init__(dispatcher, query_serializer=query_serializer)

    def bind_handlers(self, dispatcher):
        self._conv_handler = ConversationHandlerExt(
            entry_points=[],
            states={
                ANSWER_INPUT: [MessageHandler(Filters.text, self.answers_add)],
            },
            fallbacks=[CommandHandler('done', self.answers_done), ])

        dispatcher.add_handler(self._conv_handler)

    def start(self, bot, update):
        # инициируем вход(entry_points) в ConversationHandler
        self._conv_handler.set_state(update, ANSWER_INPUT)
        self.answers_start(bot, update)

    def answers_start(self, bot, update):
        """Показывает сообщение о вводе или /done для отмены
        """
        tg_message = Render().form_start().to_telegram(self._query_serializer)
        bot.send_message(chat_id=update.effective_message.chat_id,
                         **tg_message)

        return ANSWER_INPUT

    def answers_add(self, bot, update):
        tg_message = Render().form_add_answer().to_telegram(self._query_serializer)
        bot.send_message(chat_id=update.message.chat_id, **tg_message)

    def answers_done(self, bot, update):
        # parser = self._query_parser
        # query = update.callback_query
        # answers = parser.get_data(query.data)
        answers = ["За", "глу", "шка"]

        # передаем данные слушателю
        self._notify(bot, update, answers)
