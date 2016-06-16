import bson

from mongoengine.context_managers import no_dereference
from mongoengine import StringField, ListField, ReferenceField,\
    EmbeddedDocumentField

from .people import Person
from .organizations import Publisher
from .locale import Year, ISBN
from .utils import IDocument


class Source(IDocument):
    """
    A cited source of any type.
    """

    MEDIUMS = ('PRINT', 'WEB')

    title = StringField(required=True)
    medium = StringField(required=True, choices=MEDIUMS, default=MEDIUMS[0])
    description = StringField(db_field='desc')

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

    authors = ListField(ReferenceField(Person), required=True, default=[])
    editors = ListField(ReferenceField(Person), default=[])

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

    edition = StringField()
    publisher = ReferenceField(Publisher)
    published = EmbeddedDocumentField(Year, default=Year)
    location = StringField()
    isbn = EmbeddedDocumentField(ISBN, default=ISBN)

    def _serialize(self, fields):
        source = super()._serialize(fields)
        source.update({
            'edition': self.edition,
            'publisher': str(self._data['publisher'].id),
            'published': self.published.value,
            'location': self.location,
            'isbn': self.isbn.serialize(fields.get('isbn'))
        })
        return source
