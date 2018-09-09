import unittest

from votegram.handlers import (
    CallbackDataBuilderV1,
    CallbackDataParserV1,
)


class TestCallbackDataParserV1(unittest.TestCase):

    def test_get_data_correct(self):
        data = "Test data"
        correct_str = CallbackDataBuilderV1()\
            .setHandler(object)\
            .setCommand("test_func")\
            .setData(data)\
            .build()
        parse_data = CallbackDataParserV1().getData(correct_str)
        self.assertEqual(parse_data, data)

    def test_get_data_incorrect(self):
        data_str = CallbackDataBuilderV1()\
            .setHandler(object)\
            .setCommand("test_func")\
            .build()
        parse_data = CallbackDataParserV1().getData(data_str)
        self.assertEqual(len(parse_data), 0)
