import unittest

from stackcite.data import testing


class ValidationErrorTests(unittest.TestCase):

    layer = testing.layers.UnitTestLayer

    def test_default_message(self):
        from ..exceptions import ValidationError
        expected = 'Validation failed'
        error = ValidationError()
        result = error.message
        self.assertEqual(expected, result)

    def test_original_error_set(self):
        from ..exceptions import ValidationError
        orig_error = KeyError('Some key is invalid')
        error = ValidationError(original_error=orig_error)
        self.assertEqual(orig_error, error.original_error)
