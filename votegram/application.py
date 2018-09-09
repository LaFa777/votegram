from .handlers import (
    DefaultConversationHandler,
    VoteBuilderConversationHandler,
    VoteBuilderTimerConversationHandler,
)

from .vote_managers import VoteManagerMemory


class Application:
    def __init__(self, updater):
        self.updater = updater
        self.handlers = []

    def run(self):
        vote_manager = VoteManagerMemory()

        dp = self.updater.dispatcher

        self.handlers.append(DefaultConversationHandler(dp))

        voteBuilder = VoteBuilderConversationHandler(dp)
        voteBuilder.add_builder(VoteBuilderTimerConversationHandler(dp),
                                description="По таймеру")
        self.handlers.append(voteBuilder)

        # Start the Bot
        self.updater.start_polling()

        # Run the bot until the user presses Ctrl-C or the process receives
        # SIGINT, SIGTERM or SIGABRT
        self.updater.idle()
