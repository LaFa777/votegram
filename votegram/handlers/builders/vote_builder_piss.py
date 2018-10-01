from telegram_addons import (
    ComponentHandler,
)

from ..modules import (
    InputTimeComponent,
    InputTextLinesComponent,
)


class VoteBuilderPissHandler(ComponentHandler):
    """Собирает голосование против нехорошего пользователя

    Этапы:
    1. выбор времени истечения
    2. ввод имени пользователя

    TODO:
        1. Работает только в чате тет-а-тет
        2. Сделать упрощенную версию для чатов (аля /piss @user)
    """

    def __init__(self, dispatcher):
        namespace = self.__class__.__name__

        self._timer_handler = InputTimeComponent(namespace, dispatcher)
        self._answers_handler = InputTextLinesComponent(namespace, dispatcher)

        super().__init__(namespace, dispatcher)

    def bind_handlers(self, dispatcher):
        self._timer_handler.add_done_callback(self.timer_done)
        self._answers_handler.add_done_callback(self.answers_done)

    def _start(self, bot, update):
        # начинаем с запроса времени истечения голосования
        self._timer_handler.start(bot, update)

    def timer_done(self, bot, update, data):
        message = update.effective_message

        # TODO: естественно это не выводить надо, а запоминать
        bot.send_message(chat_id=message.chat_id,
                         text="Вы выбрали время {}".format(data))

        # запускаем операцию получения вариантов ответа от пользователя
        self._answers_handler.start(bot, update)

    def answers_done(self, bot, update, data):
        # TODO: естественно это не выводить надо, а запоминать
        text = "Вы ввели фразы:"
        for answer in data:
            text = text + "\n" + answer
        bot.send_message(chat_id=update.message.chat_id,
                         text=text)
