from ..telegram_utils import (
    Message,
    ButtonsMenu,
    Button,
    CallbackQueryHandlerExt,
)

from telegram.ext import (
    CommandHandler,
)

from ..handlers import (
    ModuleHandler,
)


__all__ = ("VoteBuilderConversationHandler")


class COMMAND:
    SELECT_BUILDER = "SELECT_BUILDER"


class Render:

    @staticmethod
    def form_builder(builders):
        keyboard = ButtonsMenu()
        for obj, desc in builders.items():
            data = obj.__class__.__name__
            button = Button(desc, COMMAND.SELECT_BUILDER, data)
            keyboard.add_line(button)
        return Message("Выберите тип голосования:", markup=keyboard)


class VoteSelectorBuilderHandler(ModuleHandler):

    def __init__(self, dispatcher, data_serializer=None):
        self._builders = {}
        self._render = Render()

        super().__init__(
            dispatcher,
            bind_handlers=False,
            data_serializer=data_serializer)

        self._data_serializer.set_salt(self.__class__.__name__)
        self.bind_handlers(self._dispatcher)

    def bind_handlers(self, dispatcher):
        handler = CommandHandler("start", self.show_selector)
        dispatcher.add_handler(handler)

        handler = CallbackQueryHandlerExt(COMMAND.SELECT_BUILDER, self.select_done)
        dispatcher.add_handler(handler)

    def add_builder(self, builder, description=None):
        """Добавляем обработчиков типа `VoteBuilderHandler`
        """
        # TODO: сделать проверку на isinstance(builder, VoteBuilderHandler)
        if description is None:
            description = "No description"
        self._builders[builder] = description

    def show_selector(self, bot, update):
        """Показывает форму выбора типа сборщика голосования
        """
        # TODO: выполнять только если not self._builders

        tg_message = self._render\
            .form_builder(self._builders)\
            .to_telegram(self._data_serializer)

        bot.send_message(chat_id=update.message.chat_id, **tg_message)

    def select_done(self, bot, update):
        """Инициирует начало сборки выбранного голосования.
        Удаляет сообщение с формой выбора билдера.
        """
        parser = self._data_serializer
        query = update.callback_query
        class_name = parser.loads(query.data)

        for obj in self._builders:
            if class_name == obj.__class__.__name__:
                obj.start(bot, update)
                return

    # TODO: добавить обработку когда закончится сборка Vote
