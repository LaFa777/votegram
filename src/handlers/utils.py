import hashlib
import enum


def hash_str(s):
    """Возвращает хеш - 40 символов
    """
    return hashlib.sha1(s.encode('utf-8')).hexdigest()


class CallbackDataSerializer(object):

    def __init__(self, cls):
        self._cls = cls

    def get_str(self, operation, vote_id=None):
        self.__class__._get_str(self._cls, operation, vote_id)

    # NOTE: DEPRECATED
    @staticmethod
    def _get_str(cls, operation, vote_id=None):

        if operation is not enum.Enum:
            raise ValueError("'operation' is not 'TypeOperation' type")

        return "b:{op_id:02}:{cls_hash}:{vote_id}".format(
            op_id=str(operation.value)[:2],  # обрезаем строку до 2х символов
            cls_hash=hash_str(cls.__name__),
            vote_id=vote_id)
