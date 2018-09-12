import copy

from telegram.ext import (
    Dispatcher,
)

from ..telegram_utils import (
    DispatcherProxy,
)

from .utils import (
    CallbackQuerySerializer,
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

    def __init__(self, dispatcher, bind_handlers=True, data_serializer=None):
        if data_serializer:
            self._data_serializer = copy.copy(data_serializer)
        else:
            self._data_serializer = CallbackQuerySerializer()

        self._done_callbacks = []

        dispatcher = DispatcherProxy(dispatcher, self._data_serializer)
        super().__init__(dispatcher, bind_handlers)

    def start(self, bot, update):
        """Вызвать для активации модуля
        """
        raise NotImplementedError

    # def get_data(self, bot, update):
    #     """Вычлиняет из запроса данные для модуля
    #     """

    def add_done_callback(self, callback):
        """Цепляет функцию обработчик в которую по окончанию передаются данные
        работы модуля.
        """
        self._done_callbacks.append(callback)

    def _notify(self, bot, update, data):
        for callback in self._done_callbacks:
            callback(bot, update, data)
