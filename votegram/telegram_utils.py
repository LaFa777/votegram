from telegram import (
    InlineKeyboardMarkup,
    InlineKeyboardButton,
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


# TODO: для этого есть встроенный обьект в python-telegram!!!
class Message:

    def __init__(self, text, markup=None):
        self._text = text
        self._markup = markup

    # TODO: to_dict

    def to_telegram(self, query_builder):
        reply_markup = self._markup.to_telegram(query_builder)
        return {
            "text": self._text,
            "reply_markup": reply_markup,
        }
