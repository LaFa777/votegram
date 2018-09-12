import copy

import arrow

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
    TIMER_DOWN = "TIMER.DOWN"
    TIMER_UP = "TIMER.UP"
    TIMER_DONE = "TIMER.DONE"


class Render:

    @staticmethod
    def form_timer(time, show_down=True, show_up=True, x2=False):
        # TODO: обработка ошибок, когда time не str

        # create keyboard
        buttonTimeDown = Button(text="<",
                                command=COMMAND.TIMER_DOWN,
                                data=time)

        buttonTimeUp = Button(text=">",
                              command=COMMAND.TIMER_UP,
                              data=time)

        buttonConfirm = Button(text="далее",
                               command=COMMAND.TIMER_DONE,
                               data=time)

        keyboard = ButtonsMenu()
        keyboard.add_line(buttonTimeDown, buttonConfirm, buttonTimeUp)

        # create human readable time string
        utc = arrow.utcnow()
        utc = utc.replace(seconds=int(time))
        time_str = utc.humanize(locale='ru_ru')

        text = "Окончание голосования через: {}".format(time_str)

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

    def step_up(self, time):
        if isinstance(time, str):
            time = int(time)

        index = self._TIME_STEPS.index(time)
        if (index + 1) >= len(self._TIME_STEPS):
            time = self._TIME_STEPS[index]
        else:
            time = self._TIME_STEPS[index + 1]

        return str(time)

    def step_down(self, time):
        if isinstance(time, str):
            time = int(time)

        index = self._TIME_STEPS.index(time)
        if (index - 1) < 0:
            time = self._TIME_STEPS[index]
        else:
            time = self._TIME_STEPS[index - 1]

        return str(time)

    def is_first(self, time):
        index = self._TIME_STEPS.index(time)
        if index == 0:
            return True
        else:
            return False

    def is_last(self, time):
        index = self._TIME_STEPS.index(time)
        if (index + 1) == len(self._TIME_STEPS):
            return True
        else:
            return False


class VoteConversationTimerHandler(ModuleHandler):

    def __init__(self, dispatcher, query_builder=None, query_parser=None):
        self._time_stepper = TimeStepper()

        super().__init__(
            dispatcher,
            query_builder=query_builder,
            query_parser=query_parser)

    def bind_handlers(self, dispatcher):
        # цепляем обработчик для time_down
        handler = CallbackQueryHandlerExt(COMMAND.TIMER_DOWN, self.timer_down)
        dispatcher.add_handler(handler)

        # цепляем обработчик для time_up
        handler = CallbackQueryHandlerExt(COMMAND.TIMER_UP, self.timer_up)
        dispatcher.add_handler(handler)

        # цепляем обработчик для time_done
        handler = CallbackQueryHandlerExt(COMMAND.TIMER_DONE, self.timer_done)
        dispatcher.add_handler(handler)

    def start(self, bot, update):
        # TODO: добавить параметр inplace и сделать его тут False
        self.timer_show(bot, update)

    def timer_show(self, bot, update, time=None, inplace=True):
        """Показывает сообщение с выбором времени
        """
        timer = self._time_stepper

        if time is None:
            time = timer.get_default()

        # TODO: добавить логику для показа левой и правой кнопки
        tg_message = Render()\
            .form_timer(time).\
            to_telegram(self._query_builder)

        # TODO: если inplace==False, то отправить отдельным сообщением
        query = update.callback_query.message
        bot.edit_message_text(chat_id=query.chat_id,
                              message_id=query.message_id,
                              **tg_message)

    def timer_down(self, bot, update):
        timer = self._time_stepper
        parser = self._query_parser
        query = update.callback_query

        data = parser.get_data(query.data)
        time = timer.step_down(data)
        # если время не изменялось, то ничего не делаем. (иначе вылазит ошибка)
        if data == time:
            # TODO: решить проблему с часами на кнопке
            return

        self.timer_show(bot, update, time)

    def timer_up(self, bot, update):
        timer = self._time_stepper
        parser = self._query_parser
        query = update.callback_query

        data = parser.get_data(query.data)
        time = timer.step_up(data)
        # если время не изменялось, то ничего не делаем. (иначе вылазит ошибка)
        # if data == time:
        #    # TODO: решить проблему с часами на кнопке
        #    return

        self.timer_show(bot, update, time)

    def timer_done(self, bot, update):
        """Передает посреднику время
        """
        parser = self._query_parser
        query = update.callback_query
        time = parser.get_data(query.data)

        # передаем данные слушателю
        self._notify(bot, update, time)
