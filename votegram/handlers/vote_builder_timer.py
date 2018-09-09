import arrow

from telegram import (
    InlineKeyboardMarkup,
    InlineKeyboardButton,
)

from telegram.ext import (
    CallbackQueryHandler,
)

from ..handlers import (
    BuilderHandler,
    CallbackDataBuilderV1,
    CallbackDataParserV1,
)

__all__ = ("VoteBuilderTimerConversationHandler")


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

    @staticmethod
    def get_default():
        # TODO: change to 30 min
        return TimeStepper._TIME_STEPS[2]

    @staticmethod
    def step_up(time):
        if isinstance(time, str):
            time = int(time)

        index = TimeStepper._TIME_STEPS.index(time)
        if (index + 1) >= len(TimeStepper._TIME_STEPS):
            time = TimeStepper._TIME_STEPS[index]
        else:
            time = TimeStepper._TIME_STEPS[index + 1]

        return str(time)

    @staticmethod
    def step_down(time):
        if isinstance(time, str):
            time = int(time)

        index = TimeStepper._TIME_STEPS.index(time)
        if (index - 1) < 0:
            time = TimeStepper._TIME_STEPS[index]
        else:
            time = TimeStepper._TIME_STEPS[index - 1]

        return str(time)

    @staticmethod
    def is_first(time):
        index = TimeStepper._TIME_STEPS.index(time)
        if index == 0:
            return True
        else:
            return False

    @staticmethod
    def is_last(time):
        index = TimeStepper._TIME_STEPS.index(time)
        if (index + 1) == len(TimeStepper._TIME_STEPS):
            return True
        else:
            return False


class Render:

    def __init__(self, callback_data_builder):
        self._callback_data_builder = callback_data_builder

    def show_timer(self, bot, update, callback_builder, time):
        cdata = self._callback_data_builder = callback_data_builder

        # create human readable time string
        utc = arrow.utcnow()
        utc = utc.replace(seconds=int(time))
        time_str = utc.humanize(locale='ru_ru')

        # устанавливаем данные для кнопок
        cdata.setData(time)

        callback_data = cdata.setCommand("time_down").build()
        buttonTimeDown = InlineKeyboardButton(
            text="<",
            callback_data=callback_data,
        )

        callback_data = cdata.setCommand("time_up").build()
        buttonTimeUp = InlineKeyboardButton(
            text=">",
            callback_data=callback_data,
        )

        callback_data = cdata.setCommand("time_confirm").build()
        buttonConfirm = InlineKeyboardButton(
            text="okay",
            callback_data=callback_data,
        )

        keyboard = InlineKeyboardMarkup([
            [buttonTimeDown, buttonConfirm, buttonTimeUp],
            ])

        text = "Окончание голосования через: {}".format(time_str)

        query = update.callback_query.message
        bot.edit_message_text(chat_id=query.chat_id,
                              message_id=query.message_id,
                              text=text,
                              reply_markup=keyboard)


class VoteBuilderTimerConversationHandler(BuilderHandler):

    def __init__(self,
                 dispatcher,
                 callback_data_builder,
                 callback_data_parser,
                 render=Render(),
                 time_stepper=TimeStepper()):
        self._render = render
        self._time_stepper = time_stepper
        self._callback_data_builder = callback_data_builder
        self._callback_data_parser = callback_data_parser

        super().__init__(dispatcher)

    def bind_handlers(self):
        dp = self._dispatcher
        cdb = self._callback_data_builder

        pattern = cdb.setCommand("time_down").build()
        dp.add_handler(CallbackQueryHandler(self.time_down, pattern=pattern))

        pattern = cdb.setCommand("time_up").build()
        dp.add_handler(CallbackQueryHandler(self.time_up, pattern=pattern))

    def show_timer(self, bot, update):
        """Показывает сообщение с выбором времени
        """
        timer = self._time_stepper

        time = timer.get_default()
        self._render.show_timer(bot, update, self._callback_data_builder, time)

    def time_down(self, bot, update):
        timer = self._time_stepper
        parser = self._callback_data_parser
        query = update.callback_query

        data = parser.getData(query.data)
        time = timer.step_down(data)
        # если время не изменялось, то ничего не делаем. (иначе вылазит ошибка)
        if data == time:
            return

        self._render.show_timer(bot, update, self._callback_data_builder, time)

    def time_up(self, bot, update):
        timer = self._time_stepper
        parser = self._callback_data_parser
        query = update.callback_query

        data = parser.getData(query.data)
        time = timer.step_up(data)
        # если время не изменялось, то ничего не делаем. (иначе вылазит ошибка)
        if data == time:
            return

        self._render.show_timer(bot, update, self._callback_data_builder, time)

    def time_confirm()
