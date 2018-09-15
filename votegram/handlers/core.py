import copy

from telegram.ext import (
    Dispatcher,
)

from ..telegram_utils import (
    DispatcherProxy,
    BotProxy,
)

from .utils import (
    CallbackQuerySerializer,
)

"""Потомки абстрактных классов определенных ниже добавляют обработчики в
telegram.Dispatcher. Тем самым создавая что то наподобие "дерева роутинга".
"""


class SimpleHandler:
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


class ComponentHandler(SimpleHandler):
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
                 component_name,
                 dispatcher,
                 bind_handlers=True,
                 callback_data_serializer=None):

        if callback_data_serializer:
            self._callback_data_serializer = copy.copy(callback_data_serializer)
        else:
            self._callback_data_serializer = CallbackQuerySerializer()

        self._callback_data_serializer.set_salt(component_name)

        dispatcher = DispatcherProxy(dispatcher, self._callback_data_serializer)

        self._done_callbacks = []

        super().__init__(dispatcher, bind_handlers)

    def start(self, bot, update):
        if isinstance(bot, BotProxy):
            bot = BotProxy(bot._bot, self._callback_data_serializer)
        self._start(bot, update)

    def _start(self, bot, update):
        """Каждый компонент обязан иметь данную точку входа. Вызывается из остальных классов или
        цепляется на обработчик в `.bind_handlers`.
        """
        raise NotImplementedError

    def add_done_callback(self, callback):
        """Цепляет функцию обработчик в которую по окончанию передаются данные
        работы компонента.
        """
        self._done_callbacks.append(callback)

    def _notify(self, bot, update, data):
        """Оповещает функцию обратного вызова о завершении работы компонента и передает в нее данные

        Todo: автоматически загружать переменные хранения???
        """
        if isinstance(bot, BotProxy):
            bot = BotProxy(bot._bot, self._callback_data_serializer)

        for callback in self._done_callbacks:
            callback(bot, update, data)
