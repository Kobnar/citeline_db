import unittest

from citeline import testing


class ValidationErrorTests(unittest.TestCase):
    """
    Tests for :class:`.ValidationError`.
    """
    layer = testing.layers.UnitTestLayer

    def test_default_msg(self):
        """ValidationError.__init__() sets a default `msg` string
        """
        from ..exceptions import ValidationError
        exception = ValidationError()
        self.assertIsNotNone(exception.message)
        self.assertIsInstance(exception.message, str)

    def test_msg_set(self):
        """ValidationError.__init__() can set a custom `msg` string
        """
        msg = 'Custom validation error message.'
        from ..exceptions import ValidationError
        exception = ValidationError(msg)
        self.assertEqual(exception.message, msg)

    def test_as_string(self):
        msg = 'Custom validation error message.'
        from ..exceptions import ValidationError
        exception = ValidationError(msg)
        self.assertEqual(str(exception), msg)
