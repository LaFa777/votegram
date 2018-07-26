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
    def _bot(self):
        pass

    @abstractproperty
    def _id(self):
        pass

    @abstractproperty
    def _status(self):
        pass

    @abstractproperty
    def _creator_id(self):
        pass

    @abstractproperty
    def _chat_id(self):
        pass

    @abstractproperty
    def _message_ids(self):
        pass

    @abstractproperty
    def _date_start(self):
        pass

    @abstractmethod
    def add_answer(self, update):
        pass

    # def vote(self, )

    @abstractmethod
    def update(self, update):
        self._render.update(update)
        pass

    def open(self, bot, update):
        self._status = VoteStatus.OPEN
        self._render.update()

    def close(self, bot, update):
        self._status = VoteStatus.CLOSE
        self._render.update()


class VoteEntityLimit(VoteEntity):

    def __init__(self,
                 id,
                 creator_id,
                 chat_id,
                 message_id,
                 status=VoteStatus.CLOSE):
        self._id = id
        self._status = status or VoteStatus.CLOSE
        self._creator_id = creator_id
        self._chat_id = [chat_id]
        self._message_ids = [message_id]
        self._date_start = time()
        self._answers = []

    def add_answer(self, update):
        user_id, answer = self._parser.parse(update)

        ########## добавление в память
        # self._render.add_answer(self._answers)


class VoteEntityLimitParser(object):

    @staticmethod
    def add_answer(update):
        ######### код сюда быра
        return answer_index, user_id


class VoteManager(object):

    def create(self):
        """Возвращает
        """
        raise NotImplementedError

    def get(self, id):
        """Возвращает соответствующий `VoteEntity`
        """
        raise NotImplementedError

    # def get_actives(self):
    #     """Возвращает `List[VoteEntity]` со стасуом OPEN
    #     """
    #     raise NotImplementedError


class VoteManagerInMemory(VoteManager):

    def __init__(self):
        self._votes = []
        self._id = 0

    def create(self, bot):
        self._id += 1

        return

    def get(self, id):
        return self._votes[id]


class VoteMessageParser(object):

    def parse_answer(self, update):
        pass
