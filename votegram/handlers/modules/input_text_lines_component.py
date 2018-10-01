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


class InputTextLinesRender:
    def form_start(self):
        return TextMessage("Введите свой варинт.\nОтправьте /done для окончания ввода.")

    def form_add_answer(self, text, limit_lines):
        return TextMessage("Вариант успешно добавлен. Вы можете добавить еще {} вариантов.\n"
                           "Отправьте /done для окончания ввода.".format(limit_lines))


ANSWER_INPUT = range(1)


class InputTextLinesComponent(ComponentHandler):
    """Запрашивает у пользователя варианты ответа. В data возвращает массив
    строк введенных пользователем (1 на каждое сообщение).

    Todo:
        добавить возможно удалять варианты ответа?
    """

    def __init__(self, component_name, dispatcher, limit_lines=5, render=None):
        self._conv_handler = None
        self._render = render or InputTextLinesRender()
        self._limit_lines = limit_lines
        super().__init__(component_name, dispatcher)

    def bind_handlers(self, dispatcher):
        self._conv_handler = ConversationHandlerExt(
            states={
                ANSWER_INPUT: [MessageHandler(Filters.text, self.answers_add, pass_user_data=True)],
            },
            fallbacks=[CommandHandler('done', self.answers_done, pass_user_data=True), ])
        dispatcher.add_handler(self._conv_handler)

    def _start(self, bot, update):
        self._conv_handler.set_state(update, ANSWER_INPUT)
        self.answers_start(bot, update)

    def answers_start(self, bot, update):
        tg_message = self._render.form_start()
        update.effective_message.reply_text(**tg_message)

        return ANSWER_INPUT

    def answers_add(self, bot, update, user_data={}):
        text = update.message.text

        if not user_data.get(self._component_name):
            user_data[self._component_name] = []

        user_data[self._component_name].append(text)

        left_elements = self._limit_lines - len(user_data[self._component_name])
        if left_elements <= 0:
            return self.answers_done(bot, update, user_data)
        else:
            tg_message = self._render.form_add_answer(text, left_elements)
            update.message.reply_text(**tg_message)
            return ANSWER_INPUT

    def answers_done(self, bot, update, user_data={}):
        answers = user_data.get(self._component_name, [])

        self.notify(bot, update, answers)

        return ConversationHandler.END
