from .exceptions import ValidationError


def _tokenize_isbn(isbn):
    """
    Converts a string representation of an ISBN into a list of digits.

    :param isbn: A string formatted ISBN-10 or ISBN-13
    :return: A list formatted ISBN-10 or ISBN-13
    """

    digits = []
    for digit in isbn:
        try:
            digits.append(int(digit))
        except ValueError:
            if digit is 'X':
                digits.append(10)
    return digits


def _calc_isbn10_check_digit(digits):
    """
    Calculates a valid check digit for the first nine digits of an ISBN-10.

    :param digits: A list containing the first nine digits of an ISBN-10
    :return: A valid ISBN-13 check digit
    """

    val = 0
    for idx, dgt in enumerate(digits):
        val += ((idx + 1) * dgt)
    return val % 11


def _calc_isbn13_check_digit(digits):
    """
    Calculates a valid check digit for the first twelve digits of an ISBN-13.

    :param digits: A list containing the first twelve digits of an ISBN-13
    :return: A valid ISBN-13 check digit
    """

    val = 0
    for idx, dgt in enumerate(digits):
        if not idx % 2:
            val += (dgt * 1)
        else:
            val += (dgt * 3)
    r = val % 10
    if r == 0:
        r = 10
    return 10 - r


def validate_isbn10(isbn10):
    """
    Validates an ISBN-10 by evaluating its check digit.

    :param str isbn10: A string-formatted ISBN-10
    :return str: A valid ISBN-10 string or ``None``
    """

    digits = _tokenize_isbn(isbn10)
    if len(digits) is 10:
        check_digit = digits.pop(-1)
        if check_digit is _calc_isbn10_check_digit(digits):
            return isbn10.replace('-', '')


def validate_isbn13(isbn13):
    """
    Validates an ISBN-13 by evaluating its check digit.

    :param str isbn13: A string-formatted ISBN-13
    :return str: A valid ISBN-13 string or ``None``
    """

    digits = _tokenize_isbn(isbn13)
    if len(digits) is 13:
        check_digit = digits.pop(-1)
        if check_digit is _calc_isbn13_check_digit(digits):
            return isbn13.replace('-', '')


def validate_isbn(isbn):
    """
    Validates an ISBN and returns either a validated ISBN string or ``None`` if
    the ISBN is invalid.

    :param str isbn: A string-formatted ISBN-10 or ISBN-13
    :return str: A valid ISBN string or ``None``
    """

    return validate_isbn10(isbn) or validate_isbn13(isbn)


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
