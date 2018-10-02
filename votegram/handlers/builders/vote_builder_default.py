from .core import VoteBuilder

from ..modules import (
    SelectVariantComponent,
    InputTextLinesComponent,
    SelectVariantRender,
)


class DefaultSelectVariantRender(SelectVariantRender):

    def get_text(self):
        return "Тип голосования:"


class VariantPublicity:
    anonymous = "Анонимное"
    public = "Публичное"

    @classmethod
    def list(cls):
        arr = list()
        for attribute in cls.__dict__.keys():
            if attribute[:2] != '__':
                value = getattr(cls, attribute)
                if not callable(value):
                    arr.append(value)
        return arr


class VoteBuilderDefault(VoteBuilder):
    """Собирает обычное голосование с выбором варианта ответа.
    """

    def __init__(self, component_name, dispatcher):
        namespace = component_name + "." + self.__class__.__name__

        variants = VariantPublicity.list()
        self._selector_component = SelectVariantComponent(namespace,
                                                          dispatcher,
                                                          variants,
                                                          render=DefaultSelectVariantRender())
        self._answers_component = InputTextLinesComponent(namespace, dispatcher)

        super().__init__(namespace, dispatcher)

    def bind_handlers(self, dispatcher):
        self._selector_component.add_done_callback(self.selector_done, pass_user_data=True)
        self._answers_component.add_done_callback(self.answers_done, pass_user_data=True)

    def _start(self, bot, update):
        self._selector_component.start(bot, update)

    def description(self):
        return "Обычное"

    def selector_done(self, bot, update, data, user_data):
        vote_data = user_data[self._component_name] = {}
        vote_data["publicity"] = data

        self._answers_component.start(bot, update)

    def answers_done(self, bot, update, data, user_data):
        vote_data = user_data[self._component_name]
        vote_data["answers"] = data

        self.notify(bot, update, vote_data)
