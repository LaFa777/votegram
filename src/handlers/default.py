from telegram.ext import CommandHandler

from .core import Handler


class DefaultConversationHandler(Handler):

    def bind_handlers(self):
            self.dispatcher.add_handler(CommandHandler('help', self.help))

    def help(self, bot, update):
        bot.send_message(chat_id=update.message.chat_id,
                         text="Для создания голосования введите /start")
