import unittest

from stackcite.data import testing


class StackciteErrorTestCase(unittest.TestCase):

    layer = testing.layers.UnitTestLayer

    def test_default_message(self):
        from ..exceptions import StackciteError
        expected = ''
        error = StackciteError()
        result = error.message
        self.assertEqual(expected, result)

    def test_custom_message(self):
        from ..exceptions import StackciteError
        expected = 'Something went wrong'
        error = StackciteError(expected)
        result = error.message
        self.assertEqual(expected, result)

    def test_str_returns_default_message(self):
        from ..exceptions import StackciteError
        expected = 'StackciteError'
        error = StackciteError()
        result = str(error)
        self.assertEqual(expected, result)

    def test_str_returns_custom_message(self):
        from ..exceptions import StackciteError
        message = 'Something went wrong'
        expected = 'StackciteError: {}'.format(message)
        error = StackciteError(message)
        result = str(error)
        self.assertEqual(expected, result)


class AuthenticationErrorBaseTestCase(unittest.TestCase):

    layer = testing.layers.UnitTestLayer

    def test_default_message(self):
        from ..exceptions import AuthenticationError
        expected = 'Authentication failed'
        error = AuthenticationError()
        result = error.message
        self.assertEqual(expected, result)
