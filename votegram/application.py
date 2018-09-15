from .handlers import (
    DefaultHandler,
    VoteSelectorBuilderHandler,
    VoteBuilderPissHandler,
)

from .telegram_utils import (
    DispatcherProxy,
)

# from .vote_managers import VoteManagerMemory


class Application:
    def __init__(self, updater):
        self.updater = updater

    def run(self):
        # vote_manager = VoteManagerMemory()

        dispatcher = self.updater.dispatcher

        DefaultHandler(dispatcher)

        voteBuilder = VoteSelectorBuilderHandler(dispatcher)
        voteBuilder.add_builder(VoteBuilderPissHandler(dispatcher),
                                description="Писс")

        # Start the Bot
        self.updater.start_polling()

        # Run the bot until the user presses Ctrl-C or the process receives
        # SIGINT, SIGTERM or SIGABRT
        self.updater.idle()
