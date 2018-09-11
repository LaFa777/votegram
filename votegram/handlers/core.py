from telegram.ext import (
    Dispatcher,
)

"""Потомки абстрактных классов определенных ниже изменяют/дополняют dispatcher
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

    def bind_handlers(self):
        raise NotImplementedError


class ConversationHandler(Handler):
    """Модуль для обработки более сложных взаимодействий с пользователем.

    Имеет точку входа .start(), которая имеет привелегию переключить контекст
    обработчиков в чате (например затенить существующие для получения строки
    ввода от пользователя). По окончанию работы возвращает в функцию переданную
    в add_done_callback() ранее данные о результате работы.
    """

    def __init__(self, dispatcher):
        self._done_callbacks = []
        super().__init__(dispatcher)

    def start(self, bot, update):
        """Входная точка модуля. В случае необходимости переключает обработчики.
        """
        raise NotImplementedError

    """С дальнейшим функционалом пока не определился.

    Нужно в случаях, если модуль предоставляет обратное действие.
    """

    def add_done_callback(self, callback):
        """Цепляет функцию обработчик в которую по окончанию передаются данные
        работы модуля.
        """
        self._done_callbacks.append(callback)

    def notify(self, bot, update, data):
        for callback in self._done_callbacks:
            callback(bot, update, data)
