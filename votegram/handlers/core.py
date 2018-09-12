from telegram.ext import (
    Dispatcher,
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

    def __init__(self, dispatcher):
            self._dispatcher = dispatcher
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

    def __init__(self, dispatcher):
        self._done_callbacks = []
        super().__init__(dispatcher)

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
