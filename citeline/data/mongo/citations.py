from mongoengine import StringField, ReferenceField, EmbeddedDocumentField

from .sources import Source
from .locale import PageRange
from .utils import IDocument


class Citation(IDocument):
    """
    A citation from a specific resource.
    """

    source = ReferenceField(Source)
    note = StringField()

    meta = {'allow_inheritance': True}

    def _serialize(self, fields):
        return {
            'id': str(self.id) if self.id else None,
            'source': str(self._data['source'].id),
            'note': self.note
        }


class TextCitation(Citation):
    """
    Quoted text from some kind of TextSource.
    """

    text = StringField()

    def _serialize(self, fields):
        source = super()._serialize(fields)
        source.update({
            'text': self.text
        })
        return source


class BookCitation(TextCitation):
    """
    Quoted text from a book.
    """
    pages = EmbeddedDocumentField(PageRange, default=PageRange)

    def _serialize(self, fields):
        source = super()._serialize(fields)
        source.update({
            'pages': self.pages.range,
        })
        return source
