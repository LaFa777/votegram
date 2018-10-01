from .handlers import (
    DefaultHandler,
    VoteSelectBuilderHandler,
)

from .handlers.builders import (
    VoteBuilderDefault,
    VoteBuilderSelector,
)

# from .vote_managers import VoteManagerMemory


class Application:
    def __init__(self, updater):
        self.updater = updater

    def run(self):
        # vote_manager = VoteManagerMemory()

        dispatcher = self.updater.dispatcher

        DefaultHandler(dispatcher)

        voteBuilder = VoteSelectBuilderHandler(dispatcher)
        voteBuilder.add_builder(VoteBuilderDefault(dispatcher))
        voteBuilder.add_builder(VoteBuilderSelector(dispatcher))

        # Start the Bot
        self.updater.start_polling()

        # Run the bot until the user presses Ctrl-C or the process receives
        # SIGINT, SIGTERM or SIGABRT
        self.updater.idle()
