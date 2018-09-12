import copy

from telegram.ext import (
    Dispatcher,
)

from ..telegram_utils import (
    DispatcherProxy,
)

from .utils import (
    CallbackDataBuilderV1,
    CallbackDataParserV1,
)

"""Потомки абстрактных классов определенных ниже добавляют обработчики в
telegram.Dispatcher. Тем самым создавая что то наподобие "дерева роутинга".
"""


class Handler:
    """Предназначен для обработки простейших событий.

    При субклассировании должны быть реализованы:
    1. Функция bind_handlers, цепляющая обработчики к dispatcher.
    2. Коолбеки, к которым происходит биндинг в bind_handlers
    """

    def __init__(self, dispatcher, bind_handlers=True):
            self._dispatcher = dispatcher
            if bind_handlers:
                self.bind_handlers(self._dispatcher)

    def bind_handlers(self, dispatcher):
        """Выполняет биндинг хандлеров.
        """
        raise NotImplementedError


class ModuleHandler(Handler):
    """Модуль для обработки сложных действий и возврате данных по окончанию.

    Всегда имеет точку входа `.start()` - будьте готовы, что модуль имеет полное
    право затенить существующе обработчики или немного изменить работу бота.
    (например при активации модуля получения ввода модуль начинает обрабатывать
    любой текстовый ввод от пользователя)

    По окончанию работы модуль в своей завершающей функции вызывает `notify`,
    которая в свою очередь передает всем коллбекам переданным ранее в
    `add_done_callback()` данные о результате работы. Формат даннных не
    унифицирован и индивидуален у каждого модуля (читайте в описании к модулю).
    """

    def __init__(self,
                 dispatcher,
                 bind_handlers=True,
                 query_builder=None,
                 query_parser=None,
                 query_salt=None):
        if query_builder:
            self._query_builder = copy.copy(query_builder)
        else:
            self._query_builder = CallbackDataBuilderV1()
        if query_parser:
            self._query_parser = copy.copy(query_parser)
        else:
            self._query_parser = CallbackDataParserV1()
        # устанавливаем уникальное значения для хеширования запросов
        if query_salt:
            self._query_builder.set_salt(query_salt)
            self._query_parser.set_salt(query_salt)
        self._done_callbacks = []

        dispatcher = DispatcherProxy(dispatcher, self._query_builder)
        super().__init__(dispatcher, bind_handlers)

    def start(self, bot, update):
        """Вызвать для активации модуля
        """
        raise NotImplementedError

    def add_done_callback(self, callback):
        """Цепляет функцию обработчик в которую по окончанию передаются данные
        работы модуля.
        """
        self._done_callbacks.append(callback)

    def _notify(self, bot, update, data):
        for callback in self._done_callbacks:
            callback(bot, update, data)
