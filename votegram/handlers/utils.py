import hashlib
import re
from inspect import isclass

from ..errors import (
    VotegramCallbackDataParseError,
)


def hash64(s):
    """Вычисляет хеш - 8 символов
    """
    hex = hashlib.sha1(s.encode("utf-8")).hexdigest()
    return "{:x}".format(int(hex, 16) % (10 ** 8))


class CallbackDataBuilderV1:
    """Создает строку формата "v:hash:data"
    где:
      v - номер версии (1 символ)
      hash - уникальный хеш (обработчик + метод обработки) (8 символов)
      data - данные (1-53 символа)
    """

    def __init__(self):
        self._handler = None
        self._command = None
        self._data = ""

    def setHandler(self, cls):
        self._handler = cls
        return self

    def setCommand(self, command):
        self._command = command
        return self

    def setData(self, data):
        if len(data) > 53:
            raise VotegramCallbackDataParseError

        self._data = data
        return self

    def build(self):
        if not isclass(self._handler):
            self._handler = self._handler.__class__
        base_str = self._handler.__name__ + self._command
        hash_base_str = hash64(base_str)
        return "1:{}:{}".format(hash_base_str, self._data)


class CallbackDataParserV1:

    @staticmethod
    def getData(str):
        return re.match("1:.+?:(.*)", str).group(1)
