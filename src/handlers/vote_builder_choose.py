from telegram import (
    InlineKeyboardMarkup,
    InlineKeyboardButton,
)

from telegram.ext import (
    CommandHandler,
    CallbackQueryHandler
)

from ..handlers import (
    Handler,
    builders,
    hash_inline_builder,
)


class VoteBuilderChooseConversationHandler(Handler):

    def bind_handlers(self):
        self.dispatcher.add_handler(CommandHandler("start", self.start))

    def start(self, bot, update):
        # TODO: вынести в отдельный класс рендер
        # self.render.start(bot, update)
        # create button's menu
        keyboard = []
        for cls in builders:
            keyboard.append([InlineKeyboardButton(
                    text=cls.get_description(),
                    callback_data=hash_inline_builder(cls))])

        reply_markup = InlineKeyboardMarkup(keyboard)

        bot.send_message(chat_id=update.message.chat_id,
                         text="Выберите тип голосования:",
                         reply_markup=reply_markup)
