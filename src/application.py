from .handlers import (
    DefaultConversationHandler
)


class Application:
    def __init__(self, updater):
        self.updater = updater
        self.handlers = []

    def run(self):
        self.handlers.append(
            DefaultConversationHandler(self.updater.dispatcher))

        # Start the Bot
        self.updater.start_polling()

        # Run the bot until the user presses Ctrl-C or the process receives
        # SIGINT, SIGTERM or SIGABRT
        self.updater.idle()
