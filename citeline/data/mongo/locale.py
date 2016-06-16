import re
import mongoengine

from citeline.data import validators

from . import utils


class Year(utils.IEmbeddedDocument):
    """
    A representation of a single year.
    """

    value = mongoengine.IntField(db_field='value')

    @property
    def full(self):
        """
        The full academic representation of the year (e.g. "400 B.C.E.")
        """
        if self.value < 0:
            return str(abs(self.value)) + ' B.C.E.'
        else:
            return str(self.value) + ' A.C.E.'

    def _serialize(self, fields):
        return int(self.value) if self.value else None

    def _deserialize(self, data):
        self.value = data


class ISBN(utils.IEmbeddedDocument):
    """
    An international standard book number (ISBN).

    NOTE: This class requires hyphenation.
    """

    _isbn10 = mongoengine.StringField(db_field='isbn10')
    _isbn13 = mongoengine.StringField(db_field='isbn13')

    @property
    def isbn10(self):
        """
        A non-formatted ISBN-10 number.
        """
        return self._isbn10

    @property
    def isbn13(self):
        """
        A non-formatted ISBN-13 number.
        """
        return self._isbn13

    # TODO: Convert from one ISBN to another.
    def set_isbn(self, value):
        """
        Sets a new ISBN value.
        """
        if value:
            isbn = validators.validate_isbn(value)
            if isbn:
                length = len(isbn)
                if length is 10:
                    self._isbn10 = isbn
                    # convert isbn10 to isbn13
                    # set isbn13
                else:
                    self._isbn13 = isbn
                    # convert isbn13 to isbn10
                    # set isbn10
            else:
                raise validators.ValidationError(value)
        else:
            self._isbn10 = None
            self._isbn13 = None

    def _serialize(self, fields):
        return {
            'isbn13': self.isbn13,
            'isbn10': self.isbn10
        }

    def _deserialize(self, data):
        isbn = data.get('isbn13') or data.get('isbn10')
        self.set_isbn(isbn)


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
