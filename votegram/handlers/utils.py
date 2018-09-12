import hashlib
import re
#from inspect import isclass

from ..errors import (
    VotegramCallbackDataParseError,
)


__all__ = ("CallbackQuerySerializer", )


def hash64(s):
    """Вычисляет хеш - 8 символов
    """
    hex = hashlib.sha1(s.encode("utf-8")).hexdigest()
    return "{:x}".format(int(hex, 16) % (10 ** 8))


class CallbackQuerySerializer:

    def __init__(self, salt=""):
        self._salt = salt
        self.reset()

    def reset(self):
        self._salt = ""
        self._command = None
        self._data = ""

    def set_salt(self, salt):
        self._salt = salt
        return self

    def set_command(self, command):
        self._command = command
        return self

    def set_data(self, data):
        if data is not None and len(data) >= 53:
            raise VotegramCallbackDataParseError

        self._data = data
        return self

    def dumps(self):
        """Создает строку формата "v:hash:data"
        где:
          v - номер версии (1 символ)
          hash - уникальный хеш (обработчик + метод обработки) (8 символов)
          data - данные (1-53 символа)
        """
        # TODO: сделать корректный обработчик
        #if not self._command:
        #    raise VoteQueryBuildError

        hash_str = self._salt + self._command
        hash_str = hash64(hash_str)
        return "1:{}:{}".format(hash_str, self._data)

    def loads(self, str):
        return re.match("1:.+?:(.*)", str).group(1)
