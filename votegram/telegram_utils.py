from telegram import (
    InlineKeyboardMarkup,
    InlineKeyboardButton,
)

from telegram.ext import (
    ConversationHandler,
    CallbackQueryHandler,
    Handler,
    Dispatcher,
)


class ButtonsMenu:

    def __init__(self):
        self._menu = []

    def add_line(self, *buttons):
        self._menu.append(buttons)

    def to_telegram(self, data_serializer):
        keyboard = []
        for buttons in self._menu:
            line = []
            for button in buttons:
                tg_button = button.to_telegram(data_serializer)
                line.append(tg_button)
            keyboard.append(line)
        return InlineKeyboardMarkup(keyboard)


class Button:

    def __init__(self, text, command, data=""):
        self._text = text
        self._command = command
        self._data = data

    def to_telegram(self, data_serializer):

        data = data_serializer\
                .set_command(self._command)\
                .set_data(self._data)\
                .dumps()

        button = InlineKeyboardButton(text=self._text, callback_data=data)

        return button


class Message:

    def __init__(self, text, markup=None):
        self._text = text
        self._markup = markup

    def to_telegram(self, data_serializer):
        reply_markup = None
        if self._markup is not None:
            reply_markup = self._markup.to_telegram(data_serializer)
        return {
            "text": self._text,
            "reply_markup": reply_markup,
        }


class ConversationHandlerExt(ConversationHandler):
    """Модификация оригинального `telegram.ConversationHandler` с возможностью
    установить `state`
    """

    def set_state(self, update, state):
        """Устанавливает переданный state.
        """
        # TODO: проверять наличие state в списке self._states
        key = self._get_key(update)
        self.update_state(state, key)


class HandlerExt(Handler):
    """Расширенный тип обработчиков с поддержкой преобразования команд `QueryBuilder`.
    Автоматически преобразуется `DispatcherProxy`.
    """

    def __init__(self, command, handler):
        self.command = command
        self.handler = handler


DEFAULT_GROUP = 0


class DispatcherProxy(Dispatcher):
    def __init__(self, dispatcher, data_serializer):
        self._dispatcher = dispatcher
        self._data_serializer = data_serializer

    def add_handler(self, handler, group=DEFAULT_GROUP):
        # формируем корректный pattern в случае, если это `HandlerExt`
        if isinstance(handler, HandlerExt):
            hash_str = self._data_serializer.set_command(handler.command).dumps()
            handler.handler.pattern = hash_str
            handler = handler.handler

        self._dispatcher.add_handler(handler, group)


class CallbackQueryHandlerExt(HandlerExt):
    def __init__(self,
                 command,
                 callback,
                 pass_update_queue=False,
                 pass_job_queue=False,
                 pattern=None,
                 pass_groups=False,
                 pass_groupdict=False,
                 pass_user_data=False,
                 pass_chat_data=False):
        handler = CallbackQueryHandler(
            callback,
            pass_update_queue,
            pass_job_queue,
            pattern,
            pass_groups,
            pass_groupdict,
            pass_user_data,
            pass_chat_data)
        super().__init__(command, handler)
