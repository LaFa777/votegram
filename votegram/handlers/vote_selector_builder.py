from telegram.ext import (
    CommandHandler,
)

from telegram_addons import (
    CallbackQueryHandlerExt,
    InlineKeyboardMarkupExt,
    InlineKeyboardButtonExt,
    TextMessage,
    ComponentHandler,
)


__all__ = ("VoteSelectorBuilderHandler")


class COMMAND:
    SELECT_BUILDER = "SELECT_BUILDER"


class Render:

    @staticmethod
    def form_builder(builders):
        if not builders:
            return TextMessage("Отсутствуют сборщики голосований")

        keyboard = InlineKeyboardMarkupExt()
        for obj, desc in builders.items():
            data = obj.__class__.__name__
            button = InlineKeyboardButtonExt(desc,
                                             COMMAND.SELECT_BUILDER,
                                             callback_data=data)
            keyboard.add_line(button)
        return TextMessage("Выберите тип голосования:", reply_markup=keyboard)


class VoteSelectBuilderHandler(ComponentHandler):

    def __init__(self, dispatcher, render=None):
        self._builders = {}
        self._render = render or Render()

        super().__init__(self.__class__.__name__, dispatcher)

    def bind_handlers(self, dispatcher):
        handler = CommandHandler("start", self.show_selector)
        dispatcher.add_handler(handler)

        handler = CallbackQueryHandlerExt(COMMAND.SELECT_BUILDER, self.select_done)
        dispatcher.add_handler(handler)

    def add_builder(self, builder, description=None):
        """Добавляем обработчиков типа `ModuleHandler`
        """
        builder.add_done_callback(self.building_done)

        self._builders[builder] = builder.description()

    def show_selector(self, bot, update):
        """Показывает форму выбора типа сборщика голосования
        """
        tg_message = self._render.form_builder(self._builders)

        bot.send_message(chat_id=update.message.chat_id, **tg_message)

    def select_done(self, bot, update):
        """Инициирует начало сборки выбранного голосования.
        """
        class_name = update.callback_query.data

        for obj in self._builders:
            if class_name == obj.__class__.__name__:
                obj.start(bot, update)
                update.effective_message.delete()
                return

    def building_done(self, bot, update, data):
        update.effective_message.reply_text("Голосования успешно создано")
        print(data)
