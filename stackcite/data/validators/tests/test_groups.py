import unittest

from stackcite.data import testing


class ValidateGroupUnitTests(unittest.TestCase):

    layer = testing.layers.UnitTestLayer

    def test_users_group_returns_group(self):
        """'validate_group()' accepts users group
        """
        from ..groups import validate_group
        result = validate_group('users')
        self.assertIsNotNone(result)

    def test_staff_group_returns_group(self):
        """'validate_group()' accepts staff group
        """
        from ..groups import validate_group
        result = validate_group('staff')
        self.assertIsNotNone(result)

    def test_admin_group_returns_group(self):
        """'validate_group()' accepts admin group
        """
        from ..groups import validate_group
        result = validate_group('admin')
        self.assertIsNotNone(result)

    def test_invalid_group_returns_none(self):
        """'validate_group()' rejects invalid group"""
        from ..groups import validate_group
        result = validate_group('invalid_group')
        self.assertIsNone(result)


class GroupValidatorUnitTests(unittest.TestCase):

    layer = testing.layers.UnitTestLayer

    def setUp(self):
        from ..groups import GroupValidator
        self.validator = GroupValidator()

    def test_users_group_passes(self):
        """GroupValidator accepts "users" group
        """
        from ..exceptions import ValidationError
        try:
            self.validator('users')
        except ValidationError as err:
            self.fail(err)

    def test_staff_group_passes(self):
        """GroupValidator accepts "staff" group
        """
        from ..exceptions import ValidationError
        try:
            self.validator('staff')
        except ValidationError as err:
            self.fail(err)

    def test_admin_group_passes(self):
        """GroupValidator accepts "admin" group
        """
        from ..exceptions import ValidationError
        try:
            self.validator('admin')
        except ValidationError as err:
            self.fail(err)

    def test_invalid_group_fails(self):
        """GroupValidator rejects an invalid group
        """
        from ..exceptions import ValidationError
        with self.assertRaises(ValidationError):
            self.validator('invalid')

    def test_default_msg(self):
        """GroupValidator sets a default message
        """
        invalid_group = 'invalid_group'
        from ..exceptions import ValidationError
        try:
            self.validator(invalid_group)
        except ValidationError as err:
            self.assertIsNotNone(err.message)
            self.assertIsInstance(err.message, str)

    def test_custom_msg(self):
        """GroupValidator can set a custom message
        """
        msg = 'Custom message.'
        from ..groups import GroupValidator
        validator = GroupValidator(msg)
        from ..exceptions import ValidationError
        invalid_group = 'invalid_group'
        try:
            validator(invalid_group)
        except ValidationError as err:
            self.assertEqual(err.message, msg)
