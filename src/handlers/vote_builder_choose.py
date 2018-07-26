import enum

from telegram import (
    InlineKeyboardMarkup,
    InlineKeyboardButton,
)

from telegram.ext import (
    CommandHandler,
    CallbackQueryHandler
)

from ..handlers import (
    Handler,
    Hasher,
    CallbackDataSerializer,
)

from .vote_builder_timer import VoteBuilderTimerConversationHandler

__all__ = ("VoteBuilderChooseConversationHandler")

BUILDERS = {
    "По таймеру": VoteBuilderTimerConversationHandler,
}


class OPERATION(enum.Enum):
    START_BUILDING = 1


class Render(object):

    @staticmethod
    def start(bot, update):
        # create button's menu
        keyboard = []
        for desc, cls in BUILDERS.items():

            serializer = CallbackDataSerializer(cls)
            callback_data = serializer.get_str(OPERATION.START_BUILDING)

            button = InlineKeyboardButton(
                text=desc,
                callback_data=callback_data)

            keyboard.append([button, ])

        reply_markup = InlineKeyboardMarkup(keyboard)

        bot.send_message(chat_id=update.message.chat_id,
                         text="Выберите тип голосования:",
                         reply_markup=reply_markup)


class VoteBuilderChooseConversationHandler(Handler):

    def __init__(self,
                 dispatcher,
                 render=Render):
        super().__init__(dispatcher)
        self._render = render

    def bind_handlers(self):
        self._dispatcher.add_handler(CommandHandler("start", self.start))

    def start(self, bot, update):
        self._render.start(bot, update)
