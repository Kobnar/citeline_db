import bson
import mongoengine

from . import people
from . import organizations as orgs
from . import locale
from . import utils


class Source(utils.IDocument):
    """
    A cited source of any type.
    """

    MEDIUMS = ('PRINT', 'WEB')

    title = mongoengine.StringField(required=True)
    medium = mongoengine.StringField(
        required=True, choices=MEDIUMS, default=MEDIUMS[0])
    description = mongoengine.StringField(db_field='desc')

    meta = {'allow_inheritance': True}

    def _serialize(self, fields):
        return {
            'id': str(self.id) if self.id else None,
            'title': self.title,
            'medium': self.medium,
            'description': self.description
        }


class TextSource(Source):
    """
    A cited resource containing text.
    """

    authors = mongoengine.ListField(
        mongoengine.ReferenceField(people.Person), required=True, default=[])
    editors = mongoengine.ListField(
        mongoengine.ReferenceField(people.Person), default=[])

    def _serialize(self, fields):
        source = super()._serialize(fields)
        source.update({
            'authors': [str(a.id) for a in self.authors if a.id],
            'editors': [str(e.id) for e in self.editors if e.id]
        })
        return source

    def _deserialize(self, data):
        authors = data.get('authors') or []
        editors = data.get('editors') or []
        self.authors = [bson.ObjectId(a) for a in authors]
        self.editors = [bson.ObjectId(e) for e in editors]


class BookSource(TextSource):
    """
    A cited book resource.
    """

    edition = mongoengine.StringField()
    publisher = mongoengine.ReferenceField(orgs.Publisher)
    published = mongoengine.EmbeddedDocumentField(
        locale.Year, default=locale.Year)
    location = mongoengine.StringField()
    isbn10 = locale.ISBN10Field(unique=True, sparse=True)
    isbn13 = locale.ISBN13Field(unique=True, sparse=True)

    def _serialize(self, fields):
        source = super()._serialize(fields)
        source.update({
            'edition': self.edition,
            'publisher': str(self._data['publisher'].id),
            'published': self.published.value,
            'location': self.location,
            'isbn10': self.isbn10,
            'isbn13': self.isbn13
        })
        return source
