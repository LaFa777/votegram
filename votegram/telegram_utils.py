import functools
import copy

from telegram import (
    Bot,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
    ReplyMarkup,
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

from collections import UserDict


class InlineKeyboardMarkupExt(InlineKeyboardMarkup):
    """Расширяет базовый `InlineKeyboardMarkup` возможностью отложенного построчного добавления
    кнопок.
    """

    def __init__(self, inline_keyboard=None, **kwargs):
        inline_keyboard = inline_keyboard or []
        super().__init__(inline_keyboard, **kwargs)

    def add_line(self, *buttons):
        self.inline_keyboard.append(buttons)


class InlineKeyboardButtonExt(InlineKeyboardButton):
    """Добавляет возможность более точно указать обработчика используя
    `telegram.CallbackQueryHandlerExt` путем указания параметра command (любая строка).

    Todo:
        проверять self.callback_data > 53 ???
    """

    def __init__(self, text, command, *args, **kwargs):
        self.command = command
        super().__init__(text, *args, **kwargs)

    def to_dict(self):
        if "command" in self.__dict__:
            del self.command
        return super().to_dict()

# TODO: реализовать
# class InlineKeyboardButtonMemory(InlineKeyboardButton):


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


class CallbackQueryHandlerExt:

    def __init__(self,
                 command,
                 *args,
                 **kwargs):
        self.command = command
        self.handler = CallbackQueryHandler(*args, **kwargs)


class TextMessage(UserDict):

    def __init__(self,
                 text,
                 parse_mode=None,
                 disable_web_page_preview=None,
                 disable_notification=False,
                 reply_to_message_id=None,
                 reply_markup=None,
                 timeout=None,
                 **kwargs):
        data = dict()
        data["text"] = text
        data["parse_mode"] = parse_mode
        data["disable_web_page_preview"] = disable_web_page_preview
        data["disable_notification"] = disable_notification
        data["reply_to_message_id"] = reply_to_message_id
        data["reply_markup"] = reply_markup
        data["timeout"] = timeout
        data.update(kwargs)
        self.data = data


def message_callback_data_serializer(serializer, func):
    # TODO: добавить вывод в логи информации о преобразованных хешах
    @functools.wraps(func)
    def decorator(*args, **kwargs):
        if kwargs.get('reply_markup'):
            reply_markup = kwargs.get('reply_markup')
            if isinstance(reply_markup, InlineKeyboardMarkup):
                for buttons in reply_markup.inline_keyboard:
                    for button in buttons:
                        # преобразуем callback_data для всех InlineKeyboardButtonExt
                        if isinstance(button, InlineKeyboardButtonExt):
                            prelude = serializer.set_command(button.command).dumps()
                            button.callback_data = "{hash}{data}".format(
                                hash=prelude,
                                data=button.callback_data)
                            # TODO: добавить в логгирование
                            # print("serialize: \"{}\"".format(button.callback_data))

        return func(*args, **kwargs)
    return decorator


class BotProxy:
    """Attribute proxy для `telegram.Bot`
    """

    wrapped_methods = [
        "send_message",
        "edit_message_text",
    ]

    def __init__(self, bot, callback_data_serializer=None):
        self._bot = bot
        if callback_data_serializer:
            self._callback_data_serializer = copy.copy(callback_data_serializer)
        else:
            self._callback_data_serializer = CallbackQuerySerializer()

    def __getattr__(self, name):
        if name in self.wrapped_methods:
            func = message_callback_data_serializer(
                    self._callback_data_serializer,
                    getattr(self._bot, name))
            return func
        else:
            return getattr(self._bot, name)


def message_callback_data_unserializer(serializer, func):
    # TODO: добавить вывод в логи информации о преобразованных хешах
    @functools.wraps(func)
    def decorator(bot, update):
        update.callback_query.data = serializer.loads(update.callback_query.data)
        return func(bot, update)
    return decorator


def wrapped_bot_proxy(serializer, func):
    @functools.wraps(func)
    def decorator(bot, update):
        bot = BotProxy(bot, serializer)
        return func(bot, update)
    return decorator


DEFAULT_GROUP = 0


class DispatcherProxy(Dispatcher):
    """Добавляет к диспатчеру функционал по замене объектов-контейнеров, для замены их на
    аналоги с возможностью запоминания состояния между перезапусками скрипта.
    Поддержку расширенных обработчиков (имеющих постфикс `Ext`)
    """

    def __init__(self,
                 dispatcher,
                 callback_data_serializer=None,
                 update_queue=None,
                 job_queue=None,
                 user_data=None,
                 chat_data=None,
                 conversations_data=None,
                 conversations_timeout_jobs=None):
        self._dispatcher = dispatcher
        if callback_data_serializer:
            self._callback_data_serializer = copy.copy(callback_data_serializer)
        else:
            self._callback_data_serializer = CallbackQuerySerializer()
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
        if isinstance(handler, CallbackQueryHandlerExt):
            hash_str = self._callback_data_serializer.set_command(handler.command).dumps()
            # TODO: выводить в лог
            # print("hash_str \"{}\" command \"{}\" salt \"{}\"".format(
            #     hash_str, handler.command, self._callback_data_serializer._salt))
            handler.handler.pattern = hash_str
            handler = handler.handler

            # оборачиваем callback хандлера, чтобы он автоматически зачищал маску при обработке
            handler.callback = message_callback_data_unserializer(
                self._callback_data_serializer, handler.callback)

        # в случае, если биндим `ConversationHandler`, то попытаем восстановить состояние до
        # перезапуска скрипта
        if isinstance(handler, ConversationHandler):
            if self._conversations_data is not None:
                handler.conversations = self._conversations_data
            if self._conversations_timeout_jobs is not None:
                handler.timeout_jobs = self._conversations_timeout_jobs

        # проксируем аргумент `telegram.Bot`
        if not isinstance(handler, ConversationHandler):
            handler.callback = wrapped_bot_proxy(self._callback_data_serializer, handler.callback)

        self._dispatcher.add_handler(handler, group)

    def __getattr__(self, name):
        return getattr(self._dispatcher, name)
