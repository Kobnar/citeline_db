from mongoengine import StringField, EmbeddedDocumentField

from .locale import Year
from .utils import IDocument


class Organization(IDocument):
    """
    An organization of any type.
    """

    name = StringField(required=True, unique=True)
    established = EmbeddedDocumentField(Year, db_field='est', default=Year)

    meta = {'allow_inheritance': True}

    def _serialize(self, fields):
        return {
            'id': str(self.id) if self.id else None,
            'name': self.name,
            'established': self.established.value
        }


class Publisher(Organization):
    """
    A publisher (e.g. "Random House").
    """