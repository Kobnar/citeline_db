import unittest

from citeline import testing


class SourceBaseTestCase(unittest.TestCase):

    def setUp(self):
        from ..sources import Source
        self.source = Source()
        self.source.title = 'Test Source'


class SourceUnitTestCase(SourceBaseTestCase):

    layer = testing.layers.UnitTestLayer

    def test_title_is_required(self):
        """Source.title is a required field
        """
        from ..sources import Source
        blank_resource = Source()
        from mongoengine import ValidationError
        with self.assertRaises(ValidationError):
            blank_resource.validate()

    def test_medium_default_is_print(self):
        """Source.medium default value is `Print`
        """
        self.assertEqual(self.source.medium, 'PRINT')

    def test_medium_choices_work(self):
        """Source.medium accepts valid choices
        """
        from ..sources import Source
        choices = Source.MEDIUMS
        from mongoengine import ValidationError
        for choice in choices:
            self.source.medium = choice
            try:
                self.source.validate()
            except ValidationError as err:
                self.fail(err)

    def test_validate_raises_exception_for_invalid_medium(self):
        """Source.validate() raises exception for an invalid medium
        """
        from ..sources import Source
        bad_resource = Source(medium='BADMEDIUM')
        from mongoengine import ValidationError
        with self.assertRaises(ValidationError):
            bad_resource.validate()

    def test_serialize_formats_correctly(self):
        """Source.serialize() returns a properly formatted dictionary
        """
        title = 'The Wealth of Nations'
        description = 'A book about the wealth of nations.'
        self.source.title = title
        self.source.description = description
        expected = {
            'id': None,
            'title': title,
            'medium': 'PRINT',
            'description': description}
        result = self.source.serialize()
        self.assertEqual(expected, result)


class TextSourceBaseTestCase(unittest.TestCase):

    def setUp(self):
        from ..sources import TextSource
        self.text = TextSource()
        self.text.title = 'Test TextSource'


class TextSourceUnitTestCase(TextSourceBaseTestCase):

    layer = testing.layers.UnitTestLayer

    def test_authors_required(self):
        """TextSource.authors is a required field (list cannot be empty)
        """
        from mongoengine import ValidationError
        with self.assertRaises(ValidationError):
            self.text.validate()


class TextSourceIntegrationTestCase(TextSourceBaseTestCase):

    layer = testing.layers.MongoIntegrationTestLayer

    def setUp(self):
        from ..sources import Source
        from ..people import Person
        Source.drop_collection()
        Person.drop_collection()
        super().setUp()

    def test_serialize_formats_correctly(self):
        """TextSource.serialize() returns a properly formatted dictionary
        """
        from ..people import Person
        author = Person()
        author.name.full = 'John Nobody Doe'
        author.save()

        self.text.authors.append(author)

        expected = {
            'id': None,
            'title': 'Test TextSource',
            'medium': 'PRINT',
            'description': None,
            'authors': [str(author.id)],
            'editors': []}

        result = self.text.serialize()
        self.assertEqual(expected, result)

    def test_deserialize_authors(self):
        """TextSource.deserialize() sets references to authors
        """
        full_name = 'John Nobody Doe'

        from ..people import Person
        author = Person()
        author.name.full = full_name
        author.save()

        data = {'authors': [str(author.id)]}

        self.text.deserialize(data)
        expected = full_name
        result = self.text.authors[0].name.full
        self.assertEqual(expected, result)


class BookSourceBaseTestCase(unittest.TestCase):

    def setUp(self):
        from ..sources import BookSource
        self.book = BookSource()
        self.book.title = 'Test BookSource'


class BookSourceUnitTestCase(BookSourceBaseTestCase):

    layer = testing.layers.UnitTestLayer


class BookSourceIntegrationTestCase(BookSourceBaseTestCase):

    layer = testing.layers.MongoIntegrationTestLayer

    def setUp(self):
        from ..sources import BookSource
        from ..organizations import Publisher
        from ..people import Person
        BookSource.drop_collection()
        Publisher.drop_collection()
        Person.drop_collection()
        super().setUp()

    def test_serialize_formats_correctly(self):
        """BookSource.serialize() returns a properly formatted dictionary
        """
        isbn = '9780985339890'

        from ..organizations import Publisher
        publisher = Publisher()
        publisher.name = 'Nothing House'
        publisher.save()

        from ..people import Person
        author = Person()
        author.name.full = 'John Nobody Doe'
        author.save()

        self.book.authors.append(author)
        self.book.publisher = publisher
        self.book.isbn.set_isbn(isbn)

        expected = {
            'id': None,
            'title': 'Test BookSource',
            'medium': 'PRINT',
            'description': None,
            'authors': [str(author.id)],
            'editors': [],
            'edition': None,
            'publisher': str(publisher.id),
            'published': None,
            'location': None,
            'isbn': {
                'isbn10': '0985339896',
                'isbn13': '9780985339890'
            }}

        result = self.book.serialize()
        self.assertEqual(expected, result)

    def test_deserialize_publisher(self):
        """TextSource.deserialize() sets references to authors
        """
        pub_name = 'Nothing House'
        from ..organizations import Publisher
        publisher = Publisher()
        publisher.name = pub_name
        publisher.save()
        data = {'publisher': str(publisher.id)}
        self.book.deserialize(data)
        expected = pub_name
        result = self.book.publisher.name
        self.assertEqual(expected, result)
