from .vote_builder_default import VoteBuilderDefault

from ..modules import InputTimeComponent


class VoteBuilderTimer(VoteBuilderDefault):
    """Собирает голосование со временем истечения
    """

    def __init__(self, component_name, dispatcher):
        namespace = component_name + "." + self.__class__.__name__ + "."

        self._input_time_component = InputTimeComponent(namespace, dispatcher)

        super().__init__(namespace, dispatcher)

    def bind_handlers(self, dispatcher):
        self._input_time_component.add_done_callback(self.time_done, pass_user_data=True)

        super().bind_handlers(dispatcher)

    def description(self):
        return "С таймером"

    def answers_done(self, bot, update, data, user_data):
        vote_data = user_data[self._component_name]
        vote_data["answers"] = data

        self._input_time_component.start(bot, update)

    def time_done(self, bot, update, data, user_data):
        vote_data = user_data[self._component_name]
        vote_data["end_time"] = data

        self.notify(bot, update, vote_data)
