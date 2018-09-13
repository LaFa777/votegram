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

from .handlers.utils import (
    CallbackQuerySerializer,
)


class ButtonsMenu(InlineKeyboardMarkup):

    def __init__(self):
        super().__init__([])

    def add_line(self, *buttons):
        self.inline_keyboard.append(buttons)

    def to_telegram(self, query_serializer):
        keyboard = []
        for buttons in self.inline_keyboard:
            line = []
            for button in buttons:
                tg_button = button.to_telegram(query_serializer)
                line.append(tg_button)
            keyboard.append(line)
        return InlineKeyboardMarkup(keyboard)


class Button:

    def __init__(self, text, command, data=""):
        self._text = text
        self._command = command
        self._data = data

    def to_telegram(self, query_serializer):

        data = query_serializer\
                .set_command(self._command)\
                .set_data(self._data)\
                .dumps()

        button = InlineKeyboardButton(text=self._text, callback_data=data)

        return button


class Message:

    def __init__(self, text, markup=None):
        self._text = text
        self._markup = markup

    def to_telegram(self, query_serializer):
        reply_markup = None
        if self._markup is not None:
            reply_markup = self._markup.to_telegram(query_serializer)
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
    """Добавляет к диспатчеру функционал по замене объектов-контейнеров, для замены их на
    аналоги с возможностью запоминания состояния между перезапусками скрипта.
    Поддержку расширенных обработчиков (имеющих постфикс `Ext`)
    """

    def __init__(self,
                 dispatcher,
                 query_serializer=None,
                 update_queue=None,
                 job_queue=None,
                 user_data=None,
                 chat_data=None,
                 conversations_data=None,
                 conversations_timeout_jobs=None):
        self._dispatcher = dispatcher
        self._query_serializer = query_serializer or CallbackQuerySerializer()
        # для обеспечения сохранения данных между перезапусками скрипта будем использовать
        # контейнеры-прокси, с возможностью записи на диск и загрузки с диска.
        if update_queue:
            self._dispatcher.update_queue = update_queue.update(**dispatcher.update_queue)
        if job_queue:
            self._dispatcher.job_queue = job_queue.update(**dispatcher.job_queue)
        if user_data:
            self._dispatcher.user_data = user_data.update(**dispatcher.user_data)
        if chat_data:
            self._dispatcher.chat_data = chat_data.update(**dispatcher.chat_data)
        self._conversations_data = None
        if conversations_data is not None:
            self._conversations_data = conversations_data
        self._conversations_timeout_jobs = None
        if conversations_timeout_jobs is not None:
            self._conversations_timeout_jobs = conversations_timeout_jobs

    def add_handler(self, handler, group=DEFAULT_GROUP):
        # формируем корректный pattern в случае, если это `HandlerExt`
        if isinstance(handler, HandlerExt):
            hash_str = self._query_serializer.set_command(handler.command).dumps()
            handler.handler.pattern = hash_str
            handler = handler.handler

        # в случае, если биндим `ConversationHandler`, то попытаем восстановить прошлое состояние
        if isinstance(handler, ConversationHandler):
            if self._conversations_data is not None:
                handler.conversations = self._conversations_data
            if self._conversations_timeout_jobs is not None:
                handler.timeout_jobs = self._conversations_timeout_jobs

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
