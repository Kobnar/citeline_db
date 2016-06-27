import unittest

from citeline import testing


class CiteLineErrorTestCase(unittest.TestCase):

    layer = testing.layers.UnitTestLayer

    def test_default_message(self):
        from ..exceptions import CiteLineError
        expected = ''
        error = CiteLineError()
        result = error.message
        self.assertEqual(expected, result)

    def test_custom_message(self):
        from ..exceptions import CiteLineError
        expected = 'Something went wrong'
        error = CiteLineError(expected)
        result = error.message
        self.assertEqual(expected, result)

    def test_str_returns_default_message(self):
        from ..exceptions import CiteLineError
        expected = 'CiteLineError'
        error = CiteLineError()
        result = str(error)
        self.assertEqual(expected, result)

    def test_str_returns_custom_message(self):
        from ..exceptions import CiteLineError
        message = 'Something went wrong'
        expected = 'CiteLineError: {}'.format(message)
        error = CiteLineError(message)
        result = str(error)
        self.assertEqual(expected, result)
