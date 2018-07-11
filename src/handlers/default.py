from telegram.ext import CommandHandler


class DefaultConversationHandler:

    def __init__(self, dispatcher):
            self.dispatcher = dispatcher

            self.dispatcher.add_handler(CommandHandler('start', self.start))
            self.dispatcher.add_handler(CommandHandler('help', self.help))

    def start(self, bot, update):
        bot.send_message(chat_id=update.message.chat_id, text="Hello")

    def help(self, bot, update):
        bot.send_message(chat_id=update.message.chat_id, text="/start_pool")
