import hashlib

from .core import BuilderHandler


def hash_str(s):
    """Возвращает хеш - 40 символов
    """
    return hashlib.sha1(s.encode('utf-8')).hexdigest()


def hash_inline_builder(cls):
    """Формирует строку типа `operation:start_building:hash_str:empty_19_byte`
    , где `empty_19_byte` это пустое пространство, которое можно использовать
    под свои нужды.
    """
    if not issubclass(cls, BuilderHandler):
        raise ValueError("'cls' is not 'BuilderHandler' type")

    return "t:b:{}:".format(hash_str(cls.__name__))
