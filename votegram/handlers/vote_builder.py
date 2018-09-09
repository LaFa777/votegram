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
    CallbackDataBuilderV1,
)

__all__ = ("VoteBuildeConversationHandler")


class ButtonsMenu:

    def add_line(self, buttons):


class Button:

    def __init__(self, text, data):
        self._text = text
        self._data = data


class Render(object):

    @staticmethod
    def start(bot, update, builders):
        keyboard = []

        # create button's menu
        keyboard = []
        for cls, desc in builders.items():

            callback_data = CallbackDataBuilderV1()\
                .setHandler(cls)\
                .setCommand("start")\
                .build()

            button = InlineKeyboardButton(
                text=desc,
                callback_data=callback_data)

            # IDEA: change Class on .add_line([button, ])
            keyboard.append([button, ])

        keyboard = InlineKeyboardMarkup(keyboard)

        bot.send_message(chat_id=update.message.chat_id,
                         text="Выберите тип голосования:",
                         reply_markup=keyboard)


class VoteBuilderConversationHandler(Handler):

    def __init__(self,
                 dispatcher,
                 render=None):
        self._builders = {}

        if render is None:
            render = Render()
        self._render = render

        super().__init__(dispatcher)

    def add_builder(self, builder, description=None):
        if description is None:
            description = "No description"
        self._builders[builder] = description

    def bind_handlers(self):
        self._dispatcher.add_handler(CommandHandler("start", self.start))

    def start(self, bot, update):
        self._render.start(bot, update, self._builders)
