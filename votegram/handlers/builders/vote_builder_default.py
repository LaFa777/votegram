from .core import VoteBuilder

from ..modules import (
    SelectVariantComponent,
    InputTextLinesComponent,
    SelectVariantRender,
)


class DefaultSelectVariantRender(SelectVariantRender):

    def get_text(self):
        return "Тип голосования:"


class VoteBuilderDefault(VoteBuilder):
    """Собирает обычное голосование с выбором варианта ответа.
    """

    def __init__(self, dispatcher):
        namespace = self.__class__.__name__

        variants = ["Анонимное", "Публичное"]
        self._selector_component = SelectVariantComponent(namespace,
                                                          dispatcher,
                                                          variants,
                                                          render=DefaultSelectVariantRender())
        self._answers_component = InputTextLinesComponent(namespace, dispatcher)

        super().__init__(namespace, dispatcher)

    def bind_handlers(self, dispatcher):
        self._selector_component.add_done_callback(self.selector_done)
        self._answers_component.add_done_callback(self.answers_done)

    def _start(self, bot, update):
        # коментарий
        self._selector_component.start(bot, update)

    def description(self):
        return "Обычное"

    def selector_done(self, bot, update, data):
        # TODO: естественно это не выводить надо, а запоминать
        update.effective_message.reply_text("Публичность: {}".format(data))

        # запускаем операцию получения вариантов ответа от пользователя
        self._answers_component.start(bot, update)

    def answers_done(self, bot, update, data):
        # TODO: естественно это не выводить надо, а запоминать
        text = "Варианты ответа:"
        for answer in data:
            text = text + "\n" + answer

        update.effective_message.reply_text(text)
