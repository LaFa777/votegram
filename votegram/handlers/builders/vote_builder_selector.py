from telegram_addons import (
    ComponentHandler,
)

from ..modules import (
    SelectVariantComponent,
)


class VoteBuilderSelectorHandler(ComponentHandler):

    def __init__(self, dispatcher):
        namespace = self.__class__.__name__

        variants = ["Аноним", "Паблик"]
        self._selector_handler = SelectVariantComponent(namespace, dispatcher, variants)

        super().__init__(namespace, dispatcher)

    def bind_handlers(self, dispatcher):
        self._selector_handler.add_done_callback(self.selector_done)

    def _start(self, bot, update):
        self._selector_handler.start(bot, update)

    def selector_done(self, bot, update, variant):
        update.effective_message.reply_text("Ты выбрал вариант: {}".format(variant))
