from ..telegram_utils import (
    TextMessage,
    InlineKeyboardMarkupExt,
    InlineKeyboardButtonExt,
    CallbackQueryHandlerExt,
    BotProxy,
    InlineKeyboardButtonExt,
)

from telegram.ext import (
    CommandHandler,
)

from telegram import InlineKeyboardMarkup

from ..handlers import (
    ModuleHandler,
)


__all__ = ("VoteBuilderConversationHandler")


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


class VoteSelectorBuilderHandler(ModuleHandler):

    def __init__(self, dispatcher, query_serializer=None):
        self._builders = {}
        self._render = Render()

        super().__init__(
            dispatcher,
            bind_handlers=False,
            query_serializer=query_serializer)

        self._query_serializer.set_salt(self.__class__.__name__)
        self.bind_handlers(self._dispatcher)

    def bind_handlers(self, dispatcher):
        handler = CommandHandler("start", self.show_selector)
        dispatcher.add_handler(handler)

        handler = CallbackQueryHandlerExt(COMMAND.SELECT_BUILDER, self.select_done)
        dispatcher.add_handler(handler)

    def add_builder(self, builder, description=None):
        """Добавляем обработчиков типа `ModuleHandler`
        """
        if description is None:
            description = "No description"

        self._builders[builder] = description

    def show_selector(self, bot, update):
        """Показывает форму выбора типа сборщика голосования
        """
        tg_message = self._render.form_builder(self._builders)

        bot = BotProxy(bot, self._query_serializer)
        bot.send_message(chat_id=update.message.chat_id, **tg_message)

    def select_done(self, bot, update):
        """Инициирует начало сборки выбранного голосования.
        """
        print(update.callback_query.data)
        exit()
        class_name = update.callback_query.data

        for obj in self._builders:
            if class_name == obj.__class__.__name__:
                obj.start(bot, update)
                return

    # TODO: добавить обработку когда закончится сборка Vote (пока нет смысла)
