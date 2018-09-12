from telegram import (
    InlineKeyboardMarkup,
    InlineKeyboardButton,
)

from telegram.ext import (
    ConversationHandler,
)


class ButtonsMenu:

    def __init__(self):
        self._menu = []

    def add_line(self, *buttons):
        self._menu.append(buttons)

    # TODO: to_dict

    def to_telegram(self, query_builder):
        keyboard = []
        for buttons in self._menu:
            line = []
            for button in buttons:
                tg_button = button.to_telegram(query_builder)
                line.append(tg_button)
            keyboard.append(line)
        return InlineKeyboardMarkup(keyboard)


class Button:

    def __init__(self, text, command, data=""):
        self._text = text
        self._command = command
        self._data = data

    # TODO: to_dict

    def to_telegram(self, query_builder):

        data = query_builder\
                .set_command(self._command)\
                .set_data(self._data)\
                .build()

        button = InlineKeyboardButton(
            text=self._text,
            callback_data=data)

        return button


class Message:

    def __init__(self, text, markup=None):
        self._text = text
        self._markup = markup

    # TODO: to_dict

    def to_telegram(self, query_builder):
        reply_markup = None
        if self._markup is not None:
            reply_markup = self._markup.to_telegram(query_builder)
        return {
            "text": self._text,
            "reply_markup": reply_markup,
        }


class ConversationHandlerWrapper(ConversationHandler):
    def set_state(self, update, state):
        key = self._get_key(update)
        self.update_state(state, key)
