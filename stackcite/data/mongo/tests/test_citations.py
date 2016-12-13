import unittest

from stackcite import testing


class CitationsBaseTestCase(unittest.TestCase):

    def setUp(self):
        from ..citations import Citation
        self.citation = Citation()


class CitationsUnitTestCase(CitationsBaseTestCase):

    layer = testing.layers.UnitTestLayer


class CitationsIntegrationTestCase(CitationsBaseTestCase):

    layer = testing.layers.MongoIntegrationTestLayer

    def setUp(self):
        from ..sources import Source
        from ..citations import Citation
        Source.drop_collection()
        Citation.drop_collection()
        super().setUp()

    def test_source_required(self):
        """Citation.source is a required field
        """
        from mongoengine import ValidationError
        with self.assertRaises(ValidationError):
            self.citation.validate()

    def test_serialize_source(self):
        """
        Citation.serialize() returns an accurately serialized source reference
        """
        from ..sources import Source
        source = Source()
        source.title = 'Test Source'
        source.save()

        self.citation.source = source

        expected = {
            'id': None,
            'source': str(source.id),
            'note': None}

        result = self.citation.serialize()
        self.assertEqual(expected, result)

    def test_deserialize_sets_source(self):
        """Citation.deserialize() sets the correct source
        """
        from ..sources import Source
        source = Source()
        source.title = 'Test Source'
        source.save()

        expected = source.id
        data = {'source': str(expected)}
        self.citation.deserialize(data)
        result = self.citation.source.id
        self.assertEqual(expected, result)


class TextCitationsBaseTestCase(unittest.TestCase):

    def setUp(self):
        from ..citations import TextCitation
        self.citation = TextCitation()


class TextCitationsUnitTestCase(TextCitationsBaseTestCase):

    layer = testing.layers.UnitTestLayer


class TextCitationsIntegrationTestCase(TextCitationsBaseTestCase):

    def setUp(self):
        from ..citations import TextCitation
        TextCitation.drop_collection()
        super().setUp()


class BookCitationsBaseTestCase(unittest.TestCase):

    def setUp(self):
        from ..citations import BookCitation
        self.citation = BookCitation()


class BookCitationsUnitTestCase(BookCitationsBaseTestCase):

    layer = testing.layers.UnitTestLayer


class BookCitationsIntegrationTestCase(BookCitationsBaseTestCase):

    layer = testing.layers.MongoIntegrationTestLayer

    def setUp(self):
        from ..people import Person
        from ..organizations import Publisher
        from ..sources import BookSource
        from ..citations import BookCitation
        Person.drop_collection()
        Publisher.drop_collection()
        BookSource.drop_collection()
        BookCitation.drop_collection()
        super().setUp()

    def test_serialize_returns_correct_data(self):
        """BookCitation.serialize() returns a correct dictionary of data
        """
        pages = 'pg. 123-124'

        from ..organizations import Publisher
        publisher = Publisher()
        publisher.name = 'Nobody\'s Publishing House'
        publisher.save()

        from ..people import Person
        person = Person()
        person.name.full = 'John Nobody Doe'
        person.save()

        from ..sources import BookSource
        source = BookSource()
        source.title = 'Some Book'
        source.authors.append(person)
        source.publisher = publisher
        source.save()

        self.citation.source = source
        self.citation.pages.range = pages

        expected = {
            'id': None,
            'source': str(source.id),
            'note': None,
            'text': None,
            'pages': (123, 124)}

        result = self.citation.serialize()
        self.assertEqual(expected, result)

    def test_deserialize_sets_pages(self):
        """BookCitation.deserialize() sets pages correctly
        """
        expected = (12, 13)
        data = {'pages': [12, 13]}
        self.citation.deserialize(data)
        result = self.citation.pages.range
        self.assertEqual(expected, result)
