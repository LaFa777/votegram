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

        button = InlineKeyboardButton(text=self._text, callback_data=data)

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
    def __init__(self, dispatcher, query_builder):
        self._dispatcher = dispatcher
        self._query_builder = query_builder

    def add_handler(self, handler, group=DEFAULT_GROUP):
        # формируем корректный pattern в случае, если это `HandlerExt`
        if isinstance(handler, HandlerExt):
            hash_str = self._query_builder.set_command(handler.command).build()
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
