from datetime import datetime

import bcrypt
import hashlib
import mongoengine
import os
from mongoengine import context_managers

from stackcite.data import validators
from stackcite.data.json import auth

from . import utils
from . import exceptions


class User(utils.IDocument):
    """
    A user account.
    """

    DEFAULT_GROUPS = [auth.USERS]

    email = mongoengine.EmailField(required=True, unique=True)

    _groups = mongoengine.ListField(
        mongoengine.StringField(choices=auth.GROUP_CHOICES),
        db_field='groups', required=True, default=DEFAULT_GROUPS)
    _joined = mongoengine.DateTimeField(db_field='joined', required=True)
    _last_login = mongoengine.DateTimeField(db_field='last_login')
    _prev_login = mongoengine.DateTimeField(db_field='prev_login')
    _salt = mongoengine.StringField(required=True)
    _hash = mongoengine.StringField(required=True)

    _validate_group = validators.GroupValidator()
    _validate_password = validators.PasswordValidator()

    @property
    def groups(self):
        return self._groups

    def add_group(self, group):
        self._validate_group(group)
        if group not in self.groups:
            self._groups.append(group)

    def remove_group(self, group):
        idx = self._groups.index(group)
        self._groups.pop(idx)

    @property
    def joined(self):
        return self._joined

    @property
    def last_login(self):
        return self._last_login

    @property
    def previous_login(self):
        return self._prev_login

    def touch_login(self):
        self._prev_login = self._last_login
        self._last_login = datetime.now()
        return self.last_login

    def set_password(self, new_password):
        self._validate_password(new_password)
        self._salt = self._new_salt()
        self._hash = self._encrypt(new_password)

    def check_password(self, password):
        if self._salt and self._hash:
            self._validate_password(password)
            check = self._encrypt(password)
            return self._hash == check
        else:
            return False

    @property
    def password(self):
        return bool(self._hash and self._salt)

    @password.setter
    def password(self, value):
        self.set_password(value)

    @staticmethod
    def new(email, password, save=False):
        user = User(email=email)
        user.password = password
        if save:
            user.save(cascade=True)
        return user

    @staticmethod
    def authenticate(email, password):
        user = User.objects.get(email=email)
        if user.check_password(password):
            return user
        else:
            raise exceptions.AuthenticationError()

    @staticmethod
    def _new_salt():
        return bcrypt.gensalt().decode('utf-8')

    def _encrypt(self, password):
        salt = self._salt.encode('utf-8')
        password = password.encode('utf-8')
        return bcrypt.hashpw(password, salt).decode('utf-8')

    def clean(self):
        if not self._joined:
            self._joined = datetime.now()

    def _serialize(self, fields):
        return {
            'id': str(self.id) if self.id else None,
            'email': self.email,
            'groups': self.groups,
            'joined': str(self.joined),
            'last_login': str(self.last_login)
        }


class _TokenKeyField(mongoengine.StringField):
    """
    A randomly generated string used as an API key.
    """

    _validate_key = validators.KeyValidator()

    def validate(self, value):
        super().validate(value)
        try:
            self._validate_key(value)
        except validators.ValidationError as err:
            raise mongoengine.ValidationError(err.message)


class Token(mongoengine.Document, utils.ISerializable):
    """
    An API key issued when a user logs in via api. An API token is automatically
    invalidated if it has not been "touched" in more than 1 hour.
    """

    _key = _TokenKeyField(
        primary_key=True, db_field='key', unique=True, max_length=56)
    _user = mongoengine.CachedReferenceField(
        User, required=True, unique=True, fields=('id', '_groups'))
    _issued = mongoengine.DateTimeField(db_field='issued', required=True)
    _touched = mongoengine.DateTimeField(db_field='touched', required=True)

    @staticmethod
    def gen_key():
        return hashlib.sha224(os.urandom(128)).hexdigest()

    @classmethod
    def new(cls, user, save=False):
        token = cls(_user=user)
        if save:
            token.save()
        return token

    @property
    def key(self):
        return self._key

    @property
    def user(self):
        return self._user

    @property
    def issued(self):
        return self._issued

    @property
    def touched(self):
        return self._touched

    def touch(self):
        self._touched = datetime.utcnow()
        return self.touched

    def clean(self):
        now = self.touch()
        if not self.key:
            self._key = self.gen_key()
            self._issued = now

    meta = {
        'indexes': [
            {
                'fields': ['_touched'],
                'expireAfterSeconds': 60*60  # 1 Hour
            }
        ]
    }

    def _serialize(self, fields):
        with context_managers.no_dereference(Token):
            return {
                'key': self.key,
                'user': {
                    'id': str(self.user.id) if self.user.id else None,
                    'groups': self.user.groups
                } if self.user else {},
                'issued': str(self.issued),
                'touched': str(self.touched)
            }
