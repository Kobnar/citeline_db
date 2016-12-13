import unittest

from stackcite import testing


class ValidateUsernameUnitTests(unittest.TestCase):

    layer = testing.layers.UnitTestLayer

    def test_good_usernames_return_username(self):
        """'validate_username()' accepts good usernames
        """
        good_usernames = testing.data.valid_usernames()
        from ..usernames import validate_username
        for username in good_usernames:
            username_out = validate_username(username)
            self.assertEqual(username_out, username)

    def test_bad_usernames_return_none(self):
        """'validate_username()' rejects bad usernames
        """
        bad_usernames = testing.data.invalid_usernames()
        from ..usernames import validate_username
        for username in bad_usernames:
            username_out = validate_username(username)
            self.assertIsNone(username_out)

    def test_non_usernames_fail(self):
        """'validate_username()' returns 'None' if username is 'None'
        """
        non_usernames = ['', None, False]
        from ..usernames import validate_username
        for username in non_usernames:
            self.assertEqual(validate_username(username), None)


class UsernameValidatorUnitTests(unittest.TestCase):

    layer = testing.layers.UnitTestLayer

    def setUp(self):
        from ..usernames import UsernameValidator
        self.validator = UsernameValidator()

    def test_valid_usernames_pass(self):
        """UsernameDataValidator does nothing for valid usernames
        """
        good_usernames = testing.data.valid_usernames()
        from ..exceptions import ValidationError
        for uri in good_usernames:
            try:
                self.validator(uri)
            except ValidationError as err:
                self.fail(err)

    def test_invalid_usernames_fail(self):
        """UsernameDataValidator raises exception for invalid usernames
        """
        bad_usernames = testing.data.invalid_usernames()
        from ..exceptions import ValidationError
        for uri in bad_usernames:
            with self.assertRaises(ValidationError):
                self.validator(uri)

    def test_non_string_raises_exception(self):
        """UsernameDataValidator raises exceptions for non-strings
        """
        bad_vals = [None, 123, 1.23, True, False]
        from ..exceptions import ValidationError
        for val in bad_vals:
            with self.assertRaises(ValidationError):
                self.validator(val)

    def test_default_msg(self):
        """UsernameDataValidator sets a default message
        """
        bad_username = 'bad username'
        from ..exceptions import ValidationError
        try:
            self.validator(bad_username)
        except ValidationError as err:
            self.assertIsNotNone(err.message)
            self.assertIsInstance(err.message, str)

    def test_custom_msg(self):
        """UsernameDataValidator can set a custom message
        """
        msg = 'Custom message.'
        from ..usernames import UsernameValidator
        validator = UsernameValidator(msg)
        from ..exceptions import ValidationError
        bad_username = 'bad username'
        try:
            validator(bad_username)
        except ValidationError as err:
            self.assertEqual(err.message, msg)
