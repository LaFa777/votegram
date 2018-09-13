import copy

import arrow

from telegram.error import (
    BadRequest,
)

from telegram.ext import (
    CallbackQueryHandler,
    #    CommandHandler,
)

from ...handlers import (
    ModuleHandler,
)

from ...telegram_utils import (
    Button,
    ButtonsMenu,
    Message,
    CallbackQueryHandlerExt,
)

__all__ = ("VoteConversationTimer")


class COMMAND:
    TIMER_LEFT = "TIMER.LEFT"
    TIMER_LEFT_X2 = "TIMER.LEFT_X2"
    TIMER_RIGHT = "TIMER.RIGHT"
    TIMER_RIGHT_X2 = "TIMER.RIGHT_X2"
    TIMER_DONE = "TIMER.DONE"


class Render:

    @staticmethod
    def form_timer(time, show_left=True, show_right=True, x2=False):
        # create keyboard
        line_buttons = []
        if show_left:
            if x2:
                buttonTimeLeftX2 = Button(text="<<",
                                          command=COMMAND.TIMER_LEFT_X2,
                                          data=time)
                line_buttons.append(buttonTimeLeftX2)
            buttonTimeLeft = Button(text="<",
                                    command=COMMAND.TIMER_LEFT,
                                    data=time)
            line_buttons.append(buttonTimeLeft)

        if show_right:
            buttonTimeRight = Button(text=">",
                                     command=COMMAND.TIMER_RIGHT,
                                     data=time)
            line_buttons.append(buttonTimeRight)
            if x2:
                buttonTimeRightX2 = Button(text=">>",
                                           command=COMMAND.TIMER_RIGHT_X2,
                                           data=time)
                line_buttons.append(buttonTimeRightX2)

        buttonConfirm = Button(text="далее",
                               command=COMMAND.TIMER_DONE,
                               data=time)

        keyboard = ButtonsMenu()
        keyboard.add_line(*line_buttons)
        keyboard.add_line(buttonConfirm)

        # create human readable time string
        utc = arrow.utcnow()
        utc = utc.replace(seconds=int(time))
        time_str = utc.humanize(locale='ru_ru')

        text = "Ожидаемое время завершения голосования {}".format(time_str)

        return Message(text, markup=keyboard)


class TimeStepper:

    _TIME_STEPS = [
        60,
        60 * 5 + 1,
        60 * 10 + 1,
        60 * 15 + 1,
        60 * 30 + 1,
        60 * 60 + 1,
        60 * 60 * 5 + 1,
        60 * 60 * 10 + 1,
        60 * 60 * 15 + 1,
        60 * 60 * 20 + 1,
        60 * 60 * 24 + 1,
        60 * 60 * 24 * 2 + 1,
        60 * 60 * 24 * 4 + 1,
        60 * 60 * 24 * 7 + 1,
        60 * 60 * 24 * 7 * 2 + 1,
        60 * 60 * 24 * 7 * 4 + 1,
    ]

    def get_default(self):
        # TODO: change to 30 min
        return str(self._TIME_STEPS[2])

    def step_right(self, time):
        if isinstance(time, str):
            time = int(time)

        index = self._TIME_STEPS.index(time)
        if (index + 1) >= len(self._TIME_STEPS):
            time = self._TIME_STEPS[index]
        else:
            time = self._TIME_STEPS[index + 1]

        return str(time)

    def step_left(self, time):
        if isinstance(time, str):
            time = int(time)

        index = self._TIME_STEPS.index(time)
        if (index - 1) < 0:
            time = self._TIME_STEPS[index]
        else:
            time = self._TIME_STEPS[index - 1]

        return str(time)

    def is_first(self, time):
        index = self._TIME_STEPS.index(int(time))
        if index == 0:
            return True
        else:
            return False

    def is_last(self, time):
        index = self._TIME_STEPS.index(int(time))
        if (index + 1) == len(self._TIME_STEPS):
            return True
        else:
            return False


class VoteConversationTimerHandler(ModuleHandler):

    def __init__(self, dispatcher, query_serializer):
        self._time_stepper = TimeStepper()

        super().__init__(dispatcher, query_serializer=query_serializer)

    def bind_handlers(self, dispatcher):
        # TODO: используя https://github.com/orsinium/rutimeparser предложить ввод даты пользователю

        handler = CallbackQueryHandlerExt(COMMAND.TIMER_LEFT, self.timer_left)
        dispatcher.add_handler(handler)

        handler = CallbackQueryHandlerExt(COMMAND.TIMER_LEFT_X2, self.timer_left_x2)
        dispatcher.add_handler(handler)

        handler = CallbackQueryHandlerExt(COMMAND.TIMER_RIGHT, self.timer_right)
        dispatcher.add_handler(handler)

        handler = CallbackQueryHandlerExt(COMMAND.TIMER_RIGHT_X2, self.timer_right_x2)
        dispatcher.add_handler(handler)

        handler = CallbackQueryHandlerExt(COMMAND.TIMER_DONE, self.timer_done)
        dispatcher.add_handler(handler)

    def get_data(self, update):
        """Достает время из запроса
        """
        parser = self._query_serializer

        time = ""
        if update.callback_query:
            time = parser.loads(update.callback_query.data)
        else:
            raise NotImplementedError

        return time

    def start(self, bot, update, replace_message=True):
        self.timer_show(bot, update, None, replace_message)

    def timer_show(self, bot, update, time=None, replace_message=True):
        """Показывает сообщение с выбором времени
        """
        timer = self._time_stepper

        # если время None, то устанавливаем время по умолчанию
        time = time or timer.get_default()

        # определяем, показывать ли кнопки изменения времени
        left_buttons = True
        if timer.is_first(time):
            left_buttons = False

        right_buttons = True
        if timer.is_last(time):
            right_buttons = False

        tg_message = Render()\
            .form_timer(time, left_buttons, right_buttons, True).\
            to_telegram(self._query_serializer)

        message = update.effective_message
        if replace_message:
            try:
                bot.edit_message_text(chat_id=message.chat_id,
                                      message_id=message.message_id,
                                      **tg_message)
            # скорее всего редактирование сообщения не удалось, т.к. оно такое же
            except BadRequest:
                pass
        else:
            bot.send_message(chat_id=message.chat_id,
                             **tg_message)

    def timer_left(self, bot, update):
        timer = self._time_stepper
        data = self.get_data(update)
        time = timer.step_left(data)

        self.timer_show(bot, update, time)

    def timer_left_x2(self, bot, update):
        timer = self._time_stepper
        data = self.get_data(update)
        time = timer.step_left(data)
        time = timer.step_left(time)

        self.timer_show(bot, update, time)

    def timer_right(self, bot, update):
        timer = self._time_stepper
        data = self.get_data(update)
        time = timer.step_right(data)

        self.timer_show(bot, update, time)

    def timer_right_x2(self, bot, update):
        timer = self._time_stepper
        data = self.get_data(update)
        time = timer.step_right(data)
        time = timer.step_right(time)

        self.timer_show(bot, update, time)

    def timer_done(self, bot, update):
        """Передает посреднику время
        """
        time = self.get_data(update)

        # передаем данные слушателю
        self._notify(bot, update, time)
