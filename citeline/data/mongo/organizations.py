import mongoengine

from . import locale
from . import utils


class Organization(utils.IDocument):
    """
    An organization of any type.
    """

    name = mongoengine.StringField(required=True, unique=True)
    established = mongoengine.EmbeddedDocumentField(
        locale.Year, db_field='est', default=locale.Year)

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