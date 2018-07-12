from .handlers import (
    DefaultConversationHandler,
    VoteBuilderChooseConversationHandler
)


class Application:
    def __init__(self, updater):
        self.updater = updater
        self.handlers = []

    def run(self):
        dp = self.updater.dispatcher

        self.handlers.append(DefaultConversationHandler(dp))
        self.handlers.append(VoteBuilderChooseConversationHandler(dp))

        # Start the Bot
        self.updater.start_polling()

        # Run the bot until the user presses Ctrl-C or the process receives
        # SIGINT, SIGTERM or SIGABRT
        self.updater.idle()
