import re

from . import exceptions


def validate_key(key):
    """
    Validates a given API key. Returns the initial `key` value if it is
    valid, or `None`.

    :param key: An API key string

    This validator enforces the following requirements:

    * Must be 56 characters long
    * May not include special characters
    * May not include a space (including newline characters)
    """
    if not isinstance(key, str):
        return None
    else:
        white_list = re.compile(r"^[\S]{56}$")
        spec_chars = re.escape(r"`~!@#$%^&*()+-=[]{};':\"<>,./?\|")
        black_list = re.compile(r"[" + spec_chars + r"\s\n]")
        if not white_list.search(key) or black_list.search(key):
            return None
    return key


class KeyValidator(object):
    """
    A `mongoengine` style key validator. Raises :class:`.ValidationError`
    if the key provided is invalid.
    """
    def __init__(self, msg=None):
        if msg is None:
            self.msg = 'Invalid key: {}'
        else:
            self.msg = msg

    def __call__(self, key):
        if not (isinstance(key, str) and validate_key(key)):
            raise exceptions.ValidationError(self.msg.format(key))
