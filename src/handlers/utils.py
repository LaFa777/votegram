import hashlib

from .core import BuilderHandler


def hash_str(s):
    """Возвращает хеш - 40 символов
    """
    return hashlib.sha1(s.encode('utf-8')).hexdigest()


def hash_inline_builder(cls):
    if not issubclass(cls, BuilderHandler):
        raise ValueError("'cls' is not 'BuilderHandler' type")

    # type:builder:hash_str
    return "t:b:{}".format(hash_str(cls.__name__))
