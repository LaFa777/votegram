import arrow
import rutimeparser
from datetime import datetime

from telegram.ext import (
    MessageHandler,
    Filters,
    ConversationHandler,
)

from telegram_addons import (
    ComponentHandler,
    TextMessage,
    InlineKeyboardButtonExt,
    InlineKeyboardMarkupExt,
    CallbackQueryHandlerExt,
    ConversationHandlerExt,
)

__all__ = ("VoteConversationTimer")


class COMMAND:
    TIMER_LEFT = "TIMER.LEFT"
    TIMER_LEFT_X2 = "TIMER.LEFT_X2"
    TIMER_RIGHT = "TIMER.RIGHT"
    TIMER_RIGHT_X2 = "TIMER.RIGHT_X2"
    TIMER_INPUT = "TIMER.INPUT"
    TIMER_DONE = "TIMER.DONE"


class InputTimeRender:

    def get_text_message(self):
        # TODO: при извлечении компонента из votegram обобщить текст
        return "Ожидаемое время завершения голосования {time}"

    def get_text_input(self):
        return "Ввести самому"

    def get_text_done(self):
        return "Далее"

    def message_input_start(self):
        return TextMessage("Введи фразу для определения времени.\nПримеры:\n• через пять минут\n• завтра")

    def message_input_parse_error(self):
        return TextMessage("Не могу достать дату, попробуй еще раз.")

    def message(self, time, show_left=True, show_right=True):
        # create human readable time string
        utc = arrow.utcnow()
        utc = utc.replace(seconds=int(time))
        time_str = utc.humanize(locale='ru_ru')

        text = self.get_text_message().format(time=time_str)

        keyboard = self.reply_markup(show_left, show_right)

        return TextMessage(text, reply_markup=keyboard)

    def reply_markup(self, show_left=True, show_right=True):
        line_buttons = []
        if show_left:
            buttonTimeLeftX2 = InlineKeyboardButtonExt(text="<<",
                                                       callback_data=COMMAND.TIMER_LEFT_X2)
            buttonTimeLeft = InlineKeyboardButtonExt(text="<",
                                                     callback_data=COMMAND.TIMER_LEFT)
            line_buttons.extend([buttonTimeLeftX2, buttonTimeLeft])

        if show_right:
            buttonTimeRight = InlineKeyboardButtonExt(text=">",
                                                      callback_data=COMMAND.TIMER_RIGHT)
            buttonTimeRightX2 = InlineKeyboardButtonExt(text=">>",
                                                        callback_data=COMMAND.TIMER_RIGHT_X2)
            line_buttons.extend([buttonTimeRight, buttonTimeRightX2])

        buttonInput = InlineKeyboardButtonExt(text=self.get_text_input(),
                                              command=COMMAND.TIMER_INPUT)

        buttonConfirm = InlineKeyboardButtonExt(text=self.get_text_done(),
                                                command=COMMAND.TIMER_DONE)

        keyboard = InlineKeyboardMarkupExt()
        keyboard.add_line(*line_buttons)
        keyboard.add_line(buttonInput)
        keyboard.add_line(buttonConfirm)

        return keyboard


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

    def in_range(self, time):
        low = self._TIME_STEPS[0]
        max = self._TIME_STEPS[-1]

        return (low < time < max)


TEXT_INPUT = range(1)


class InputTimeComponent(ComponentHandler):
    """Компонент для ввода времени
    """

    def __init__(self, namespace, dispatcher, render=None, time_stepper=None):
        self._time_stepper = time_stepper or TimeStepper()
        self._render = render or InputTimeRender()
        self._conv_handler = None

        component_name = namespace + "_input_time"

        super().__init__(component_name, dispatcher)

    def bind_handlers(self, dispatcher):
        # TODO: используя https://github.com/orsinium/rutimeparser предложить ввод даты пользователю
        # ну то есть добавить кнопку для ручного ввода даты

        handler = CallbackQueryHandlerExt(callback=self.timer_show, pass_user_data=True)
        dispatcher.add_handler(handler)

        handler = CallbackQueryHandlerExt(COMMAND.TIMER_DONE, self.timer_done, pass_user_data=True)
        dispatcher.add_handler(handler)

        handler = CallbackQueryHandlerExt(COMMAND.TIMER_INPUT, callback=self.timer_input_start)
        dispatcher.add_handler(handler)

        self._conv_handler = ConversationHandlerExt(states={
                TEXT_INPUT: [MessageHandler(Filters.text, self.timer_input_proccess, pass_user_data=True)],
            })
        dispatcher.add_handler(self._conv_handler)

    def _start(self, bot, update, replace_message=False):
        self.timer_show(bot, update, replace_message=replace_message)

    def timer_show(self, bot, update, user_data={}, replace_message=True):
        # алиасы
        stepper = self._time_stepper
        message = update.effective_message

        # загрузим реальное значение времени
        time = user_data.get(self._component_name) or stepper.get_default()

        # в случае, если передана команда, то изменим время
        command = None
        if update.callback_query:
            command = update.callback_query.data

        if command == COMMAND.TIMER_LEFT_X2:
            time = stepper.step_left(time)
            time = stepper.step_left(time)
        elif command == COMMAND.TIMER_LEFT:
            time = stepper.step_left(time)
        elif command == COMMAND.TIMER_RIGHT:
            time = stepper.step_right(time)
        elif command == COMMAND.TIMER_RIGHT_X2:
            time = stepper.step_right(time)
            time = stepper.step_right(time)

        # сохраняем время
        user_data[self._component_name] = time

        # определяем, показывать ли кнопки изменения времени
        left_buttons = not stepper.is_first(time)
        right_buttons = not stepper.is_last(time)

        # генерируем сообщение
        tg_message = self._render.message(time, left_buttons, right_buttons)

        # отправляем сообщение
        if replace_message:
                message.edit_text(**tg_message)
        else:
            message.reply_text(**tg_message)

    def timer_input_start(self, bot, update):
        """Начало ручного ввода даты
        """
        message = update.effective_message

        self._conv_handler.set_state(update, TEXT_INPUT)

        # генерируем сообщение
        tg_message = self._render.message_input_start()

        message.edit_text(**tg_message)

    def timer_input_proccess(self, bot, update, user_data):
        text = update.message.text

        time_now = datetime.now()
        parse_time = rutimeparser.parse(text, now=time_now, allowed_results=(datetime, None))

        # неудачный разбор времени
        if not parse_time:
            tg_message = self._render.message_input_parse_error()
            update.message.reply_text(**tg_message)
            return TEXT_INPUT

        seconds = (parse_time - time_now).total_seconds()

        # TODO: проверять в time_steppere на принадлежность к диапозону
        # if self._time_stepper.in_range(seconds):
        #   tg_message = self._render.message_input_parse_range_error()
        #   update.message.reply_text(**tg_message)
        #   return TEXT_INPUT

        self.notify(bot, update, seconds)

        return ConversationHandler.END

    def timer_done(self, bot, update, user_data):
        update.effective_message.delete()
        time = user_data.get(self._component_name) or self._time_stepper.get_default()
        self.notify(bot, update, time)
