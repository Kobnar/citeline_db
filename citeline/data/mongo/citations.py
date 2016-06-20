import mongoengine

from . import sources
from . import locale
from . import utils


class Citation(utils.IDocument):
    """
    A citation from a specific resource.
    """

    source = mongoengine.ReferenceField(sources.Source, required=True)
    note = mongoengine.StringField()

    meta = {'allow_inheritance': True}

    def _serialize(self, fields):
        return {
            'id': str(self.id) if self.id else None,
            'source': str(self._data['source'].id),
            'note': self.note
        }

    def _deserialize(self, data):
        super()._deserialize(data)
        source_id = data.get('source')
        if source_id:
            self.source = sources.Source.objects.get(id=source_id)


class TextCitation(Citation):
    """
    Quoted text from some kind of TextSource.
    """

    text = mongoengine.StringField()

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
    pages = mongoengine.EmbeddedDocumentField(
        locale.PageRange, default=locale.PageRange)

    def _serialize(self, fields):
        source = super()._serialize(fields)
        source.update({
            'pages': self.pages.range,
        })
        return source

    def _deserialize(self, data):
        self.pages.range = data.pop('pages')
        super()._deserialize(data)
