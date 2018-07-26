import arrow

from telegram.ext import (
    CallbackQueryHandler,
)

from ..handlers import (
    BuilderHandler,
    CallbackDataSerializer,
)

__all__ = ("VoteBuilderTimerConversationHandler")


class OPERATION(enum.Enum):
    CHOOSE_TIME = 1  # START_BUILDING


class RENDER(object):

    _TIME_STEPS = [
        60,
        60 * 5 + 1,
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

    def __init__(self):
        self.time = self._TIME_STEPS[9]

    def increase(self):
        index = self._TIME_STEPS.index(self.time)
        if (index + 1) >= len(index):
            return False
        else:
            self.time = self._TIME_STEPS[index + 1]
            return self.time

    def decrease(self):
        index = self._TIME_STEPS.index(self.time)
        if (index - 1) < 0:
            return False
        else:
            self.time = self._TIME_STEPS[index - 1]
            return self.time

    def show(self, bot, update):
        # create human readable time string
        utc = arrow.utcnow()
        utc = utc.replace(seconds=self.time)
        time = utc.humanize(locale='ru_ru')

        # create button's menu
        keyboard = [[
            InlineKeyboardButton(
                text="<",
                callback_data=,
            ),
            InlineKeyboardButton(
                text=">",
                callback_data=,
            ),
        ], [
            InlineKeyboardButton(
                text="okay",
                callback_data=,
            ),
        ]]
        keyboard.append([InlineKeyboardButton(
                    text=cls.get_description(),
                    callback_data=hash_inline_builder(cls))])

        bot.send_message()


class VoteBuilderTimerConversationHandler(BuilderHandler):

    def __init__(self,
                 dispatcher,
                 render=Render):
        super().__init__(dispatcher)
        self._render = render

    def bind_handlers(self):
        dp = self._dispatcher

        serializer = CallbackDataSerializer(self)

        with self:
            pattern = serializer.get_str(OPERATION.CHOOSE_TIME)
            dp.add_handler(CallbackQueryHandler(choose_time, pattern=pattern))

    def choose_time(self, bot, update):
