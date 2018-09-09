import unittest

from votegram import (
    VotegramCallbackDataParseError,
)

from votegram.handlers import (
    CallbackDataBuilderV1,
)


class TestCallbackDataParserV1(unittest.TestCase):

    def test_get_data_overflow_data(self):
        len_55 = "qwertyuiopasdfghjklzxcvbnm123456789qwertyuiopasdfghjklz"
        with self.assertRaises(VotegramCallbackDataParseError):
            CallbackDataBuilderV1().setData(len_55)
