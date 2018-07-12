from ..handlers import BuilderHandler


class VoteBuilderTimerConversationHandler(BuilderHandler):

    def bind_handlers(self):
        self.dispatcher()

    def choose_time(self, bot, update):
        time_start

        # TODO: вынести в отдельный класс рендер
        # self.render.choose_time(bot, update)
        # create button's menu
        keyboard = [[
            InlineKeyboardButton(
                text="<",
                callback_data=,
            ),
            InlineKeyboardButton(
                text=time_start,
            ),
            InlineKeyboardButton(
                text=">",
                callback_data=,
            ),
        ], [
            InlineKeyboardButton(
                text="okay",
                callback_data=,
            ),
        ]]
        keyboard.append([InlineKeyboardButton(
                    text=cls.get_description(),
                    callback_data=hash_inline_builder(cls))])

        bot.send_message()

    @staticmethod
    def _hash_inline_btn

    @classmethod
    def get_description(cls):
        return "По таймеру"
