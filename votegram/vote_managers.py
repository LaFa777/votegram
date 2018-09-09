class VoteManager(object):

    def create(self, vote_cls):
        """
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


class VoteManagerMemory(VoteManager):

    def __init__(self):
        self._votes = {}
        self._id = 0

    def create(self, vote_cls):
        # TODO: выброс исключения
        # if vote_cls is not Vote:
            # вывод ошибки
        vote = vote_cls(self._id)
        self._votes[self._id] = vote
        self._id = self._id + 1
        return vote

    def get(self, id):
        return self._votes[id]
