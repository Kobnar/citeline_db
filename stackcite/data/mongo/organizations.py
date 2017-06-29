import mongoengine

from . import locale
from . import utils


class Organization(utils.IDocument):
    """
    An organization of any type.
    """

    name = mongoengine.StringField(required=True, unique=True)
    established = mongoengine.IntField()
    description = mongoengine.StringField()

    meta = {'allow_inheritance': True}

    def _serialize(self, fields):
        return {
            'id': str(self.id) if self.id else None,
            'name': self.name,
            'established': self.established,
            'description': self.description
        }


class Publisher(Organization):
    """
    A publisher (e.g. "Random House").
    """

    region = mongoengine.StringField(max_length=2)

    def _serialize(self, fields):
        org = super()._serialize(fields)
        org.update({
            'region': self.region
        })
        return org
