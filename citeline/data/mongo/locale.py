import re
import mongoengine

from citeline.data import validators

from . import utils


class ISBN10Field(mongoengine.StringField):
    """
    An ISBN-10 string.
    """

    def validate(self, value):
        super().validate(value)
        if not validators.validate_isbn10(value):
            msg = '{} is not a valud ISBN-10'
            self.error(msg.format(value))


class ISBN13Field(mongoengine.StringField):
    """
    An ISBN-13 string.
    """

    def validate(self, value):
        super().validate(value)
        if not validators.validate_isbn13(value):
            msg = '{} is not a valud ISBN-13'
            self.error(msg.format(value))


class PageRange(utils.IEmbeddedDocument):
    """
    The page number component of a valid citation (e.g. "pg. 105-106")
    """

    start = mongoengine.IntField(db_field='start', required=True)
    end = mongoengine.IntField(db_field='end')

    @property
    def range(self):
        """
        A 2-tuple set of start and end values for a range of pages.

        This property can accept either a single integer (indicating a single
        page), a 2-tuple of integers (indicating both a starting and ending
        page number) or a string containing an integer or hyphenated integer
        pair (e.g. "103-104").

        If the start value provided is larger than the end value, setter will
        raise a :class:`ValueError` exception.
        """
        return self.start, self.end

    @range.setter
    def range(self, value):

        # Sets single integer:
        if isinstance(value, int):
            start = value
            end = None

        # Sets tuple or list:
        elif isinstance(value, (tuple, list)):
            if len(value) is not 2:
                msg = 'len(PageNumber.pages) must equal "2"'
                raise ValueError(msg)
            start, end = value

        # Parses values from string:
        elif isinstance(value, str):
            results = re.search(r'(\d+)-?(\d+)?', value)
            if results:
                start, end = results.groups()
            else:
                msg = 'Could not find valid page numbers in "{}"'.format(value)
                raise ValueError(msg)

        # Raises TypeError if none of the above:
        else:
            msg = 'PageNumber.pages must be an integer, tuple or properly' \
                  'formatted string'
            raise TypeError(msg)

        # Raises ValueError if start value is greater than end value
        if (start and end) and (start > end):
            msg = '"start" value ({}) cannot be greater than "end" value ({})'\
                .format(start, end)
            raise ValueError(msg)

        # Sets properties:
        self.start, self.end = int(start), int(end) if end else None

    def __str__(self):
        pages = [str(p) for p in (self.start, self.end) if p]
        return 'pg. {}'.format('-'.join(pages))

    def _serialize(self, fields):
        return self.start, self.end
