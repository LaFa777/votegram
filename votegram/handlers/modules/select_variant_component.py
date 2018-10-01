from telegram_addons import (
    ComponentHandler,
    TextMessage,
    InlineKeyboardButtonExt,
    InlineKeyboardMarkupExt,
    CallbackQueryHandlerExt,
)


class COMMAND:
    SELECTOR_CHOOSE = "SELECTOR.CHOOSE"


class SelectVariantRender:

    def get_text(self):
        return "Выбери вариант:"

    def form(self, variants):
        keyboard = InlineKeyboardMarkupExt()
        for index, variant in enumerate(variants):
            button = InlineKeyboardButtonExt(text=variant,
                                             callback_data=str(index))
            keyboard.add_line(button)

        text = self.get_text()

        return TextMessage(text, reply_markup=keyboard)


class SelectVariantComponent(ComponentHandler):

    def __init__(self, component_name, dispatcher, variants, render=None):
        self._render = render or SelectVariantRender()
        self._variants = variants
        super().__init__(component_name, dispatcher)

    def bind_handlers(self, dispatcher):
        handler = CallbackQueryHandlerExt(callback=self.selector_done)
        dispatcher.add_handler(handler)

    def _start(self, bot, update, replace_message=False):
        self.selector_show(bot, update, replace_message)

    def selector_show(self, bot, update, replace_message=True):
        tg_message = self._render.form(self._variants)

        # отправляем сообщение
        message = update.effective_message
        if replace_message:
            message.edit_text(**tg_message)
        else:
            message.reply_text(**tg_message)

    def selector_done(self, bot, update):
        update.effective_message.delete()

        index = int(update.callback_query.data)

        try:
            variant = self._variants[index]
            self.notify(bot, update, variant)
        except IndexError:
            # если произошла подмена индекса, то ничего не делаем
            pass
