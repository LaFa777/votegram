from time import time
from abc import ABCMeta, abstractmethod, abstractproperty
from enum import Enum


class VoteStatus(Enum):
    OPEN = 0
    CLOSE = 1


# на разных фотках
# кнопки
# текст новый
class VoteEntity(metaclass=ABCMeta):

    @abstractproperty
    def id(self):
        pass

    @abstractproperty
    def status(self):
        pass

    def __init__(self, id, creator_id, chat_id, message_id, status):
        self.id = id
        self.status = status or VoteStatus.CLOSE
        self.creator_id = creator_id
        self.chat_id = [chat_id]
        self.message_ids = [message_id]
        self.date_start = time()
        self.answers = []

    def add_answer(self, index, user_id):

    def send_pending_msg(self, bot, update):
        # вместо кнопок отображает мол пока низзя голосовать
        pass

    def open(self, bot, update):

    def close(self, bot, update):


class VoteManager(metaclass=ABCMeta):

    def create(self):
        """Возвращает
        """
        raise NotImplementedError

    def get(self, id):
        """Возвращает соответствующий `VoteEntity`
        """
        raise NotImplementedError

    def get_actives(self):
        """Возвращает `List[VoteEntity]` со стасуом OPEN
        """
        raise NotImplementedError


class VoteManagerMemory(VoteManager):

    def __init__(self):
        self.votes = []

    def create(self):
        return
