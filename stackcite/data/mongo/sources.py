import bson
import mongoengine

from stackcite import data as db

from . import people
from . import organizations as orgs
from . import locale
from . import utils


class Source(utils.IDocument):
    """
    A cited source of any type.
    """

    TYPES = ('SOURCE', 'TEXT', 'BOOK')
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
        super()._deserialize(data)
        # Get author and editor ObjectId lists
        author_ids = data.get('authors')
        editor_ids = data.get('editors')
        # Create a single query set from both lists
        all_ids = (author_ids or []) + (editor_ids or [])
        all_ppl = db.Person.objects(id__in=all_ids)
        # Add authors and editors to list if they were set
        if author_ids:
            self.authors = [a for a in all_ppl if str(a.id) in author_ids]
        if editor_ids:
            self.editors = [e for e in all_ppl if str(e.id) in editor_ids]


class BookSource(TextSource):
    """
    A cited book resource.
    """

    edition = mongoengine.StringField()
    publisher = mongoengine.ReferenceField(orgs.Publisher)
    published = mongoengine.IntField()
    location = mongoengine.StringField()
    isbn10 = locale.ISBN10Field(unique=True, sparse=True)
    isbn13 = locale.ISBN13Field(unique=True, sparse=True)

    def _serialize(self, fields):
        source = super()._serialize(fields)
        source.update({
            'edition': self.edition,
            'publisher': str(self._data['publisher'].id) if self.publisher else None,
            'published': self.published,
            'location': self.location,
            'isbn10': self.isbn10,
            'isbn13': self.isbn13
        })
        return source
