import unittest

import mongoengine

from stackcite import testing


def make_user(email, password=None, clean=True, save=False):
    from .. import auth
    user = auth.User(email=email)
    if password:
        user.set_password(password)
    if save:
        user.save()
    return user


def make_auth_token(user, clean=True, save=False):
    from .. import auth
    token = auth.AuthToken(_user=user)
    if save:
        token.save()
    return token


def make_conf_token(user, clean=True, save=False):
    from .. import auth
    token = auth.ConfirmToken(_user=user)
    if save:
        token.save()
    return token


class TokenKeyFieldTestCase(unittest.TestCase):

    layer = testing.layers.UnitTestLayer

    def setUp(self):
        from ..auth import TokenKeyField
        self.field = TokenKeyField()

    def test_validate_accepts_valid_isbn10s(self):
        """TokenKeyField.validate() accepts a valid token key
        """
        valid_key = '2107d2510eee901146dad0b54ef67176726a790f68ce240065296b71'
        from mongoengine import ValidationError
        try:
            self.field.validate(valid_key)
        except ValidationError as err:
            self.fail(err)

    def test_validate_raises_exception_for_invalid_isbns(self):
        """TokenKeyField.validate() raises exception for invalid token key
        """
        invalid_key = 'derp'
        from mongoengine import ValidationError
        with self.assertRaises(ValidationError):
            self.field.validate(invalid_key)


class UserBaseTestCase(unittest.TestCase):

    def setUp(self):
        from .. import auth
        self.user = auth.User()


class UserUnitTestCase(UserBaseTestCase):

    layer = testing.layers.UnitTestLayer
    
    def test_email_is_required(self):
        """User.email is a required field
        """
        try:
            self.user.validate()
        except mongoengine.ValidationError as err:
            err_dict = err.to_dict()
            invalid_fields = err_dict.keys()
            self.assertIn('email', invalid_fields)

    def test_joined_is_required(self):
        """User.joined is a required field
        """
        try:
            self.user.validate(clean=False)
        except mongoengine.ValidationError as err:
            err_dict = err.to_dict()
            invalid_fields = err_dict.keys()
            self.assertIn('_joined', invalid_fields)

    def test_set_password_call_is_required(self):
        """User.set_password() call is required to validate document
        """
        try:
            self.user.validate()
        except mongoengine.ValidationError as err:
            err_dict = err.to_dict()
            invalid_fields = err_dict.keys()
            self.assertIn('_salt', invalid_fields)
            self.assertIn('_hash', invalid_fields)

    def test_group_default_is_empty_list(self):
        """User.groups defaults to an empty list
        """
        self.assertEqual(self.user.groups, [])

    def test_groups_is_read_only(self):
        """User.groups is read-only
        """
        with self.assertRaises(AttributeError):
            self.user.groups = ['users', 'admins']

    def test_add_group_adds_valid_group(self):
        """User.add_group() adds a valid group
        """
        from stackcite.data.json import auth
        try:
            self.user.add_group(auth.STAFF)
        except ValueError as err:
            msg = 'Unexpected exception raised: {}'
            self.fail(msg.format(err))

    def test_add_group_does_not_add_duplicate_group(self):
        """User.add_group() will not add a duplicate group
        """
        from stackcite.data.json import auth
        self.user.add_group(auth.USERS)
        expected = [auth.USERS]
        result = self.user.groups
        self.assertEqual(expected, result)

    def test_remove_group_removes_valid_group(self):
        """User.remove_group() removes a valid group
        """
        from stackcite.data.json import auth
        self.user.add_group('staff')
        try:
            self.user.remove_group(auth.STAFF)
        except ValueError as err:
            msg = 'Unexpected exception raised: {}'
            self.fail(msg.format(err))

    def test_add_group_raises_exception_for_invalid_group(self):
        """User.add_group() raises exception for invalid group
        """
        from stackcite.data import validators
        with self.assertRaises(validators.ValidationError):
            self.user.add_group('invalid')

    def test_remove_group_raises_exception_if_not_in_group(self):
        """User.remove_group() raises exception if not in group
        """
        with self.assertRaises(ValueError):
            self.user.remove_group('invalid')

    def test_joined_is_read_only(self):
        """User.joined is read-only
        """
        from datetime import datetime
        with self.assertRaises(AttributeError):
            self.user.joined = datetime.now()

    def test_confirmed_is_read_only(self):
        """User.confirmed is read-only
        """
        from datetime import datetime
        with self.assertRaises(AttributeError):
            self.user.confirmed = datetime.now()

    def test_confirm_sets_confirmed(self):
        """User.confirm() sets User.confirmed field
        """
        self.user.confirm()
        result = self.user.confirmed
        self.assertIsNotNone(result)

    def test_confirm_adds_default_group(self):
        """User.confirm() adds user to default group
        """
        self.user.confirm()
        from ..auth import User
        default_groups = User.DEFAULT_GROUPS
        for g in default_groups:
            self.assertIn(g, self.user.groups)

    def test_last_login_is_read_only(self):
        """User.last_login is read-only
        """
        from datetime import datetime
        with self.assertRaises(AttributeError):
            self.user.last_login = datetime.now()

    def test_prev_login_is_read_only(self):
        """User.prev_login is read-only
        """
        from datetime import datetime
        with self.assertRaises(AttributeError):
            self.user.previous_login = datetime.now()

    def test_touch_login_sets_last_login(self):
        """User.touch_login() sets 'last_login'
        """
        self.user.touch_login()
        self.assertIsNotNone(self.user.last_login)

    def test_second_touch_login_sets_new_last_login(self):
        """User.touch_login() sets new 'last_login' if called twice
        """
        self.user.touch_login()
        first_login = self.user.last_login
        import time
        time.sleep(0.01)
        self.user.touch_login()
        self.assertNotEqual(first_login, self.user.last_login)

    def test_first_touch_login_does_not_set_previous_login(self):
        """User.touch_login() does not change 'previous_login' if called once
        """
        self.user.touch_login()
        self.assertIsNone(self.user.previous_login)

    def test_second_touch_login_sets_previous_login(self):
        """User.touch_login() changes 'previous_login' if called twice
        """
        self.user.touch_login()
        self.user.touch_login()
        self.assertIsNotNone(self.user.previous_login)

    def test_touch_login_sets_previous_login_to_last_login(self):
        """User.touch_login() sets 'previous_login' to original 'last_login'
        """
        from itertools import repeat
        for _ in repeat(None, 3):
            self.user.touch_login()
            first_login = self.user.last_login
            import time
            time.sleep(0.01)
            self.user.touch_login()
            self.assertEqual(first_login, self.user.previous_login)

    def test_set_password_passes_validation_with_valid_passwords(self):
        """User.set_password() accepts valid passwords
        """
        from stackcite.testing import data
        test_data = data.valid_passwords()
        for valid_password in test_data:
            try:
                self.user.set_password(valid_password)
            except mongoengine.ValidationError as err:
                msg = 'Unexpected exception raised: {}'
                self.fail(msg.format(err))

    def test_set_password_fails_validation_with_invalid_passwords(self):
        """User.set_password() raises exception for invalid passwords
        """
        from stackcite.testing import data
        test_data = data.invalid_passwords()
        from stackcite.data import validators
        for invalid_password in test_data:
            with self.assertRaises(validators.ValidationError):
                self.user.set_password(invalid_password)

    def test_check_password_returns_false_if_password_not_set(self):
        """User.check_password() returns false if password has not been set
        """
        result = self.user.check_password('T3stPa$$word')
        self.assertFalse(result)

    def test_check_password_fails_validation_with_invalid_passwords(self):
        """User.check_password() raises exception for invalid passwords
        """
        self.user.set_password('T3stPa$$word')
        from stackcite.testing import data
        test_data = data.invalid_passwords()
        from stackcite.data import validators
        for invalid_password in test_data:
            with self.assertRaises(validators.ValidationError):
                self.user.check_password(invalid_password)

    def test_check_password_matches_correct_passwords(self):
        """User.check_password() returns True for correct passwords
        """
        from stackcite.testing import data
        test_data = data.valid_passwords()
        for password in test_data:
            self.user.set_password(password)
            result = self.user.check_password(password)
            self.assertTrue(result)

    def test_check_password_fails_incorrect_passwords(self):
        """User.check_password() returns False for incorrect passwords
        """
        from stackcite.testing import data
        test_data = data.valid_passwords()
        for password in test_data:
            self.user.set_password(password)
            result = self.user.check_password('Wr0ngPa$$word')
            self.assertFalse(result)

    def test_password_passes_validation_with_valid_passwords(self):
        """User.password setter accepts valid passwords
        """
        try:
            self.user.password = 'T3stPa$$word'
        except mongoengine.ValidationError as err:
            msg = 'Unexpected exception raised: {}'
            self.fail(msg.format(err))

    def test_password_fails_validation_with_invalid_passwords(self):
        """User.password setter raises exception for invalid passwords
        """
        from stackcite.data import validators
        with self.assertRaises(validators.ValidationError):
            self.user.password = 'invalid_password'

    def test_password_returns_false_if_no_password_set(self):
        """User.password getter returns False if no password has been set
        """
        self.assertFalse(self.user.password)

    def test_password_returns_true_if_password_set(self):
        """User.password getter returns True if password has been set
        """
        self.user.password = 'T3stPa$$word'
        self.assertTrue(self.user.password)

    def test_clean_sets_joined(self):
        """User.clean() sets 'joined' field
        """
        self.user.clean()
        self.assertIsNotNone(self.user.joined)

    def test_clean_does_not_change_joined_on_addl_saves(self):
        """User.clean() does not change 'joined' if called more than once
        """
        self.user.clean()
        first_dtg = self.user.joined
        import time
        time.sleep(0.01)
        self.user.clean()
        second_dtg = self.user.joined
        self.assertEqual(first_dtg, second_dtg)


class UserIntegrationTestCase(UserBaseTestCase):

    layer = testing.layers.MongoIntegrationTestLayer

    def setUp(self):
        from .. import auth
        auth.User.drop_collection()
        super().setUp()
        
    def test_email_is_unique(self):
        """User.email
        """
        from .. import auth
        self.user.email = 'test@email.com'
        self.user.set_password('T3stPa$$word')
        self.user.save()
        dup_user = auth.User()
        dup_user.email = 'test@email.com'
        dup_user.set_password('T3stPa$$word')
        with self.assertRaises(mongoengine.NotUniqueError):
            dup_user.save()

    def test_new_does_not_save_if_save_not_set(self):
        """User.new() does not save new user by default
        """
        from .. import auth
        user = auth.User.new('test@email.com', 'T3stPa$$word')
        self.assertIsNone(user.id)

    def test_new_saves_user_if_save_set(self):
        """User.new() saves data if 'save=True'
        """
        from .. import auth
        user = auth.User.new('test@email.com', 'T3stPa$$word', True)
        self.assertIsNotNone(user.id)

    def test_authenticate_correct_password_returns_user(self):
        """User.authenticate() returns user for correct password
        """
        self.user.email = 'test@email.com'
        self.user.set_password('T3stPa$$word')
        self.user.save()
        from .. import auth
        result = auth.User.authenticate(self.user.email, 'T3stPa$$word')
        self.assertEqual(self.user, result)

    def test_authenticate_incorrect_password_raises_exception(self):
        """User.authenticate() raises exception for incorrect password
        """
        self.user.email = 'test@email.com'
        self.user.set_password('T3stPa$$word')
        self.user.save()
        from .. import auth
        from ..exceptions import AuthenticationError
        with self.assertRaises(AuthenticationError):
            auth.User.authenticate(self.user.email, 'Wr0ngPa$$word')

    def test_serialize_returns_correct_dict(self):
        """User.serialize() returns an accurate dictionary
        """
        self.maxDiff = None
        import bson
        user_id = self.user.id = bson.ObjectId()
        self.user.email = 'test@email.com'
        self.user.set_password('T3stPa$$word')
        last_login = self.user.touch_login()
        self.user.clean()
        expected = {
            'id': str(user_id),
            'email': 'test@email.com',
            'groups': [],
            'joined': str(self.user.joined),
            'last_login': str(last_login),
        }
        result = self.user.serialize()
        self.assertEqual(expected, result)

    def test_serialize_returns_filtered_dict(self):
        """User.serialize() returns a filtered dictionary if 'fields' are provided
        """
        self.maxDiff = None
        import bson
        user_id = self.user.id = bson.ObjectId()
        self.user.email = 'test@email.com'
        self.user.set_password('T3stPa$$word')
        last_login = self.user.touch_login()
        self.user.save()
        fields = ['id', 'email', 'groups',
                  'last_login']
        expected = {
            'id': str(user_id),
            'email': self.user.email,
            'groups': [],
            'last_login': str(last_login)
        }
        result = self.user.serialize(fields)
        self.assertEqual(expected, result)


class AuthTokenBaseTestCase(unittest.TestCase):
    pass


class AuthTokenUnitTestCase(AuthTokenBaseTestCase):

    layer = testing.layers.UnitTestLayer

    def setUp(self):
        user = make_user('test@email.com')
        self.api_token = make_auth_token(user)

    def test_key_is_readonly(self):
        """AuthToken.key field is read-only
        """
        with self.assertRaises(AttributeError):
            self.api_token.key = '7bd8a259670a9577dc473bf4c9ef91db787aa34cad8f0ce62b93a4fe'

    def test_user_is_readonly(self):
        """AuthToken.user field is read-only
        """
        with self.assertRaises(AttributeError):
            self.api_token.user = make_user('test@email.com')

    def test_issued_is_readonly(self):
        """AuthToken.issued field is read-only
        """
        from datetime import datetime
        with self.assertRaises(AttributeError):
            self.api_token.issued = datetime.utcnow()

    def test_touched_is_readonly(self):
        """AuthToken.touched field is read-only
        """
        from datetime import datetime
        with self.assertRaises(AttributeError):
            self.api_token.touched = datetime.utcnow()

    def test_key_set_on_clean(self):
        """AuthToken.clean() sets AuthToken.key field
        """
        self.assertIsNone(self.api_token.key)
        self.api_token.clean()
        self.assertIsNotNone(self.api_token.key)

    def test_issued_set_on_clean(self):
        """AuthToken.clean() sets AuthToken.issued field
        """
        self.assertIsNone(self.api_token.issued)
        self.api_token.clean()
        self.assertIsNotNone(self.api_token.issued)

    def test_issued_static_on_clean(self):
        """AuthToken.clean() does not change AuthToken.issued field
        """
        self.api_token.clean()
        expected = self.api_token.issued
        for _ in range(5):
            self.api_token.clean()
            result = self.api_token.issued
            self.assertEqual(expected, result)

    def test_touched_set_on_clean(self):
        """AuthToken.clean() sets AuthToken.touched field
        """
        self.assertIsNone(self.api_token.touched)
        self.api_token.clean()
        self.assertIsNotNone(self.api_token.touched)

    def test_touched_updates_on_clean(self):
        """AuthToken.clean() updates AuthToken.touched field with a different value
        """
        from time import sleep
        self.api_token.clean()
        expected = self.api_token.touched
        for _ in range(5):
            sleep(0.5)
            self.api_token.clean()
            result = self.api_token.touched
            self.assertNotEqual(expected, result)

    def test_touch_updates_touched(self):
        """AuthToken.touch() sets AuthToken.touched field
        """
        self.assertIsNone(self.api_token.touched)
        self.api_token.touch()
        self.assertIsNotNone(self.api_token.touched)

    def test_invalid_key_raises_exception(self):
        """AuthToken() raises exception for invalid key string
        """
        from datetime import datetime
        from ..auth import AuthToken
        from mongoengine import ValidationError
        user = self.api_token.user
        invalid_token = AuthToken(
            _user=user,
            _key='A bad token',
            _issued=datetime.utcnow())
        with self.assertRaises(ValidationError):
            invalid_token.validate()


class AuthTokenIntegrationTestCase(AuthTokenBaseTestCase):

    layer = testing.layers.MongoIntegrationTestLayer

    def setUp(self):
        from .. import auth
        auth.User.drop_collection()
        auth.AuthToken.drop_collection()
        self.user = auth.User.new('test@email.com', 'T3stPa$$word')
        self.api_token = auth.AuthToken.new(self.user)

    def test_user_is_not_unique(self):
        """AuthToken.user is not a unique field
        """
        self.user.save()
        from .. import auth
        auth.AuthToken.new(self.user, save=True)
        import mongoengine
        try:
            auth.AuthToken.new(self.user, save=True)
        except mongoengine.NotUniqueError as err:
            self.fail(err)

    def test_new_saves_token_to_db_if_specified(self):
        """AuthToken.new() saves new token to database if 'save=True' is set"""
        self.user.save()
        from .. import auth
        key = auth.AuthToken.new(self.user, save=True).key
        import mongoengine
        try:
            auth.AuthToken.objects.get(_key=key)
        except mongoengine.DoesNotExist as err:
            msg = 'Unexpected exception raised: {}'
            self.fail(msg.format(err))

    def test_serialize_returns_accurate_dict(self):
        """AuthToken.serialize() returns an accurate dictionary
        """
        self.user.save()
        self.api_token.clean()
        expected = {
            'key': self.api_token.key,
            'user': {
                'id': str(self.user.id),
                'groups': []
            },
            'issued': str(self.api_token.issued),
            'touched': str(self.api_token.touched)
        }
        result = self.api_token.serialize()
        self.assertEqual(expected, result)

    def test_serialized_performs_zero_queries(self):
        """AuthToken.serialize() performs zero database queries
        """
        from mongoengine import context_managers
        self.api_token.user.save()
        self.api_token.save()
        expected = 0
        with context_managers.query_counter() as result:
            self.api_token.serialize()
            self.assertEqual(expected, result)


class ConfirmTokenBaseTestCase(unittest.TestCase):
    pass


class ConfirmTokenUnitTestCase(ConfirmTokenBaseTestCase):

    layer = testing.layers.UnitTestLayer

    def setUp(self):
        user = make_user('test@email.com', 'T3stPa$$word')
        self.conf_token = make_conf_token(user)

    def test_key_is_readonly(self):
        """ConfirmToken.key field is read-only
        """
        with self.assertRaises(AttributeError):
            self.conf_token.key = '7bd8a259670a9577dc473bf4c9ef91db787aa34cad8f0ce62b93a4fe'

    def test_user_is_readonly(self):
        """ConfirmToken.user field is read-only
        """
        with self.assertRaises(AttributeError):
            self.conf_token.user = make_user('test@email.com')

    def test_issued_is_readonly(self):
        """ConfirmToken.issued field is read-only
        """
        from datetime import datetime
        with self.assertRaises(AttributeError):
            self.conf_token.issued = datetime.utcnow()

    def test_key_set_on_clean(self):
        """ConfirmToken.clean() sets ConfirmToken.key field
        """
        self.assertIsNone(self.conf_token.key)
        self.conf_token.clean()
        self.assertIsNotNone(self.conf_token.key)

    def test_issued_set_on_clean(self):
        """ConfirmToken.clean() sets ConfirmToken.issued field
        """
        self.assertIsNone(self.conf_token.issued)
        self.conf_token.clean()
        self.assertIsNotNone(self.conf_token.issued)

    def test_issued_static_on_clean(self):
        """ConfirmToken.clean() does not change ConfirmToken.issued field
        """
        self.conf_token.clean()
        expected = self.conf_token.issued
        for _ in range(5):
            self.conf_token.clean()
            result = self.conf_token.issued
            self.assertEqual(expected, result)

    def test_invalid_key_raises_exception(self):
        """ConfirmToken() raises exception for invalid key string
        """
        from datetime import datetime
        from ..auth import ConfirmToken
        from mongoengine import ValidationError
        user = self.conf_token.user
        invalid_token = ConfirmToken(
            _user=user,
            _key='A bad token',
            _issued=datetime.utcnow())
        with self.assertRaises(ValidationError):
            invalid_token.validate()


class ConfirmTokenIntegrationTestCase(ConfirmTokenBaseTestCase):

    layer = testing.layers.MongoIntegrationTestLayer

    def setUp(self):
        from .. import auth
        auth.User.drop_collection()
        auth.ConfirmToken.drop_collection()
        self.user = make_user('test@email.com', 'T3stPa$$word')
        self.conf_token = auth.ConfirmToken.new(self.user)

    def test_new_saves_token_to_db_if_specified(self):
        """ConfirmToken.new() saves new token to database if 'save=True' is set
        """
        self.user.save()
        from .. import auth
        key = auth.ConfirmToken.new(self.user, save=True).key
        import mongoengine
        try:
            auth.ConfirmToken.objects.get(_key=key)
        except mongoengine.DoesNotExist as err:
            msg = 'Unexpected exception raised: {}'
            self.fail(msg.format(err))

    def test_confirm_sets_user_confirm_field_true(self):
        """ConfirmToken.confirm() sets associated User.confirmed field to 'True'
        """
        self.conf_token.confirm_user()
        result = self.user.confirmed
        self.assertTrue(result)

    def test_confirm_saves_user_confirm_to_database(self):
        """ConfirmToken.confirm() saves user confirmation to database
        """
        self.user.save()
        self.conf_token.confirm_user()
        from stackcite import data as db
        result = db.User.objects.get(id=self.user.id).confirmed
        self.assertTrue(result)

    def test_confirm_deletes_confirmation_token(self):
        """ConfirmToken.confirm() deletes confirmation token if successful
        """
        self.user.save()
        self.conf_token.save()
        key = self.conf_token.key
        self.conf_token.confirm_user()
        import mongoengine
        from stackcite import data as db
        with self.assertRaises(mongoengine.DoesNotExist):
            db.ConfirmToken.objects.get(_key=key)

    def test_confirm_returns_user(self):
        """ConfirmToken.confirm() returns associated User object
        """
        self.user.save()
        self.conf_token.save()
        expected = self.user.id
        result = self.conf_token.confirm_user().id
        self.assertEqual(expected, result)

    def test_serialize_returns_accurate_dict(self):
        """ConfirmToken.serialize() returns an accurate dictionary
        """
        self.user.save()
        self.conf_token.clean()
        expected = {
            'key': self.conf_token.key,
            'user': {
                'id': str(self.user.id)
            },
            'issued': str(self.conf_token.issued)
        }
        result = self.conf_token.serialize()
        self.assertEqual(expected, result)

    def test_serialized_performs_zero_queries(self):
        """ConfirmToken.serialize() performs zero database queries
        """
        from mongoengine import context_managers
        self.conf_token.user.save()
        self.conf_token.save()
        expected = 0
        with context_managers.query_counter() as result:
            self.conf_token.serialize()
            self.assertEqual(expected, result)
