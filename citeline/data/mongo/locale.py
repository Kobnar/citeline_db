from mongoengine import IntField, StringField

from citeline.data import validators

from .utils import IEmbeddedDocument


class Year(IEmbeddedDocument):
    """
    A representation of a single year.
    """
    value = IntField(required=True, db_field='value')

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


class ISBN(IEmbeddedDocument):
    """
    An international standard book number (ISBN).

    NOTE: This class requires hyphenation.
    """
    _isbn10 = StringField(db_field='isbn10')
    _isbn13 = StringField(db_field='isbn13')

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
