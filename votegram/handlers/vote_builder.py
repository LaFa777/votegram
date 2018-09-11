from ..telegram_utils import (
    Message,
    ButtonsMenu,
    Button,
)

from telegram.ext import (
    CommandHandler,
    CallbackQueryHandler,
)

from ..handlers import (
    Handler,
    CallbackDataBuilderV1,
    CallbackDataParserV1,
)


__all__ = ("VoteBuilderConversationHandler")


class COMMAND:
    CHOOSE_BUILDER = "CHOOSE_BUILDER"


class Render:

    @staticmethod
    def form_builder(builders):
        keyboard = ButtonsMenu()
        for obj, desc in builders.items():
            class_name = obj.__class__.__name__
            button = Button(desc,
                            command=COMMAND.CHOOSE_BUILDER,
                            data=class_name)
            keyboard.add_line(button)
        return Message("Выберите тип голосования:", markup=keyboard)


class VoteBuilderHandler(Handler):

    def __init__(self, dispatcher):
        self._builders = {}
        self._query_builder = CallbackDataBuilderV1()
        self._query_builder.set_salt(self.__class__.__name__)
        self._query_parser = CallbackDataParserV1()
        self._query_parser.set_salt(self.__class__.__name__)
        self._render = Render()

        super().__init__(dispatcher)

    def add_builder(self, builder, description=None):
        if description is None:
            description = "No description"
        self._builders[builder] = description

    def bind_handlers(self, dispatcher):
        handler = CommandHandler("start", self.show_selection_form)
        dispatcher.add_handler(handler)

        pattern = self._query_builder\
            .set_command(COMMAND.CHOOSE_BUILDER)\
            .build()
        handler = CallbackQueryHandler(self.envoke_building, pattern=pattern)
        dispatcher.add_handler(handler)

    def show_selection_form(self, bot, update):
        """Показывает форму выбора типа сборщика голосования
        """
        # TODO: выполнять только если not self._builders

        tg_message = self._render\
            .form_builder(self._builders)\
            .to_telegram(self._query_builder)

        bot.send_message(chat_id=update.message.chat_id,
                         **tg_message)

    def envoke_building(self, bot, update):
        """Инициирует начало сборки выбранного голосования.
        Удаляет сообщение с формой выбора билдера.
        """
        # TODO: удалять сообщение из которого пришел запрос (с выбором билдера)
        parser = self._query_parser
        query = update.callback_query
        class_name = parser.get_data(query.data)

        for obj in self._builders:
            if class_name == obj.__class__.__name__:
                obj.start(bot, update)
                return
