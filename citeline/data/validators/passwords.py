import re

from . import exceptions


def validate_password(password):
    """
    Validates a given password. Returns the initial ``password`` string if
    the password is good and ``None`` if the password fails validation.

    :param str password: A password string.

    This validator enforces the following requirements:

    * 8-50 characters long.
    * Contains at-least one lower-case letter.
    * Contains at-least one upper-case letter.
    * Contains at-least one digit.
    * Contains at-least one basic symbol.
    """
    if not isinstance(password, str):
        return None
    else:
        spec_chars = re.escape("`~!@#$%^&*()_+-=[]{};':\"<>,./?\|")
        rules = [
            re.compile(r"^[\s\S]{8,50}$"),
            re.compile(r"[a-z]"),
            re.compile(r"[A-Z]"),
            re.compile(r"[0-9]"),
            re.compile(r"[" + spec_chars + r"]")
            ]
        for rule in rules:
            if not rule.search(password):
                return None
    return password


class PasswordValidator(object):
    """
    A `mongoengine` style password validator. Raises :class:`.ValidationError`
    if the password provided is invalid.
    """
    def __init__(self, msg=None):
        if msg is None:
            self.msg = 'Invalid Password: {}'
        else:
            self.msg = msg

    def __call__(self, password):
        if not (isinstance(password, str) and validate_password(password)):
            raise exceptions.ValidationError(self.msg.format(password))
