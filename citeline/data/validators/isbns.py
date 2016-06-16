from .exceptions import ValidationError


def _validate_isbn10(digits):
    """
    Validates an ISBN-10 by checking its check code.

    :param list digits: A list of 10 digits
    :return bool: ``True`` if ``digits`` is a valid ISBN-10, ``False`` if not
    """
    val = 0
    for idx, dgt in enumerate(digits):
        val += ((idx + 1) * dgt)
    if not val % 11:
        return True
    else:
        return False


def _validate_isbn13(digits):
    """
    Validates an ISBN-13 by checking its check code.

    :param list digits: A list of 13 digits
    :return bool: ``True`` if ``digits`` is a valid ISBN-13, ``False`` if not
    """
    check_digit = digits.pop(-1)
    val = 0
    for idx, dgt in enumerate(digits):
        if not idx % 2:
            val += (dgt * 1)
        else:
            val += (dgt * 3)
    rmndr = val % 10
    if rmndr == 0:
        rmndr = 10
    if 10 - rmndr == check_digit:
        return True
    else:
        return False


def validate_isbn(isbn):
    """
    Validates an ISBN and returns either a validated ISBN string or ``None`` if
    the ISBN is invalid.

    :param str isbn: An ISBN
    :return: A validated ISBN string or ``None`` if invalid
    """
    if not isinstance(isbn, str):
        return None

    isbn = isbn.replace('-', '')

    # Handle 'X' check bit
    digits = [x for x in isbn]
    if digits[-1] == 'X':
        digits[-1] = 10

    try:
        digits = [int(x) for x in digits]
    except ValueError:
        return

    if len(digits) == 10 and _validate_isbn10(digits):
        return isbn
    if len(digits) == 13 and _validate_isbn13(digits):
        return isbn


class ISBNValidator(object):
    """
    A `mongoengine` style ISBN validator. Raises :class:`.ValidationError` if
    the ISBN provided is invalid. Automatically detects the difference between
    ISBN-10 and ISBN-13 formatted strings.
    """
    def __init__(self, msg=None):
        if msg is None:
            self.msg = 'Invalid ISBN: {}'
        else:
            self.msg = msg

    def __call__(self, isbn):
        if not (isinstance(isbn, str) and validate_isbn(isbn)):
            raise ValidationError(self.msg.format(isbn))
