from telegram.ext import (
    CommandHandler,
    MessageHandler,
    Filters,
    ConversationHandler,
)

from telegram_addons import (
    ComponentHandler,
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


class VoteConvesationAnswersHandler(ComponentHandler):
    """Запрашивает у пользователя варианты ответа. В data возвращает массив
    строк введенных пользователем (1 на каждое сообщение).

    Todo:
      добавить возможность удаления ответов?
      ограничение по количеству добавляемых ответов
    """

    def __init__(self, component_name, dispatcher, render=None):
        self._conv_handler = None
        self._render = render or Render()
        super().__init__(component_name, dispatcher)

    def bind_handlers(self, dispatcher):
        # TODO: заменить на AnyTextInputHandler ???
        self._conv_handler = ConversationHandlerExt(
            states={
                ANSWER_INPUT: [MessageHandler(Filters.text, self.answers_add)],
            },
            fallbacks=[CommandHandler('done', self.answers_done), ])

        dispatcher.add_handler(self._conv_handler)

    def _start(self, bot, update):
        self._conv_handler.set_state(update, ANSWER_INPUT)
        self.answers_start(bot, update)

    def answers_start(self, bot, update):
        """Показывает сообщение о вводе или /done для отмены
        """
        tg_message = Render().form_start()
        update.effective_message.reply_text(**tg_message)

        return ANSWER_INPUT

    def answers_add(self, bot, update):
        tg_message = Render().form_add_answer()
        update.message.reply_text(**tg_message)

    def answers_done(self, bot, update):
        # parser = self._query_parser
        # query = update.callback_query
        # answers = parser.get_data(query.data)
        answers = ["За", "глу", "шка"]

        # передаем данные слушателю
        self.notify(bot, update, answers)

        return ConversationHandler.END
