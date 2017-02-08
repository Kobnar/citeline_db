import unittest

from stackcite.data import testing


class GenKeyTestCase(unittest.TestCase):

    layer = testing.layers.UnitTestLayer

    def test_returns_56_char_key(self):
        from .. import utils
        result = utils.gen_key()
        self.assertEqual(56, len(result))


class ISerializableBaseTestCase(unittest.TestCase):

    def setUp(self):
        from .. import utils
        self.doc = utils.ISerializable()


class ISerializableUnitTestCase(ISerializableBaseTestCase):

    layer = testing.layers.UnitTestLayer

    def test_serialize_raises_exception(self):
        """ISerializeable.serialize() raises NotImplementedError
        """
        with self.assertRaises(NotImplementedError):
            self.doc.serialize()

    def test_parse_fields_none_converts_to_dict(self):
        """parse_fields() converts None to dict
        """
        fields = None
        expected = {}
        result = self.doc.parse_fields(fields)
        self.assertEqual(expected, result)

    def test_parse_fields_empty_tuple_converts_to_dict(self):
        """parse_fields() converts empty tuple to dict
        """
        fields = ()
        expected = {}
        result = self.doc.parse_fields(fields)
        self.assertEqual(expected, result)

    def test_parse_fields_empty_dict_remains_empty(self):
        """parse_fields() does not effect empty dict
        """
        fields = {}
        expected = {}
        result = self.doc.parse_fields(fields)
        self.assertEqual(expected, result)

    def test_parse_fields_first_level_strings(self):
        """parse_fields() parses first-level strings correctly (e.g. 'author')
        """
        fields = ('this', 'that')
        expected = {
            'this': {}, 'that': {}}
        result = self.doc.parse_fields(fields)
        self.assertEqual(expected, result)

    def test_parse_fields_second_level_strings(self):
        """parse_fields() parses second-level strings correctly (e.g. 'author.name')
        """
        fields = ('this',
                  'that.this', 'that.that')
        expected = {
            'this': {}, 'that': {
                'this': {}, 'that': {}}}
        result = self.doc.parse_fields(fields)
        self.assertEqual(expected, result)

    def test_parse_fields_third_level_strings(self):
        """parse_fields() parses third-level strings correctly (e.g. 'author.name.first')
        """
        fields = ('this',
                  'that.this',
                  'that.that.this', 'that.that.that')
        expected = {
            'this': {}, 'that': {
                'this': {}, 'that': {
                    'this': {}, 'that': {}}}}
        result = self.doc.parse_fields(fields)
        self.assertEqual(expected, result)

    def test_parse_fields_realistic_condition(self):
        """parse_fields() parses a realistic third-level string assignment correctly
        """
        fields = ('author.name.first',
                  'author.name.last',
                  'published')
        expected = {
            'author': {
                'name': {
                    'first': {},
                    'last': {}}},
            'published': {}}
        result = self.doc.parse_fields(fields)
        self.assertEqual(expected, result)

    def test_parse_fields_multiple_iterations_do_nothing(self):
        """parse_fields() does not change results after multiple iterations
        """
        fields = ('this',
                  'that.this',
                  'that.that.this', 'that.that.that')
        expected = {
            'this': {}, 'that': {
                'this': {}, 'that': {
                    'this': {}, 'that': {}}}}
        result = self.doc.parse_fields(fields)
        for i in range(10):
            result = self.doc.parse_fields(result)
        self.assertEqual(expected, result)


class ISerializableIntegrationTestCase(ISerializableBaseTestCase):

    layer = testing.layers.MongoIntegrationTestLayer


class IDeserializableBaseTestCase(unittest.TestCase):

    def setUp(self):
        from .. import utils
        self.doc = utils.IDeserializable()


class IDeserializableUnitTestCase(IDeserializableBaseTestCase):

    layer = testing.layers.UnitTestLayer


class IDeserializableIntegrationTestCase(IDeserializableBaseTestCase):

    layer = testing.layers.MongoIntegrationTestLayer


class IEmbeddedDocumentBaseTestCase(unittest.TestCase):

    def setUp(self):
        from .. import utils
        self.embed_doc = utils.IEmbeddedDocument()


class IEmbeddedDocumentUnitTestCase(IEmbeddedDocumentBaseTestCase):

    layer = testing.layers.UnitTestLayer

    def test_serializable(self):
        try:
            self.embed_doc.serialize()
        except NotImplementedError:
            pass
        except AttributeError as err:
            msg = 'Unexpected exception raised: {}'
            self.fail(msg.format(err))


class IEmbeddedDocumentIntegrationTestCase(IEmbeddedDocumentBaseTestCase):

    layer = testing.layers.MongoIntegrationTestLayer


class IDocumentBaseTestCase(unittest.TestCase):

    def setUp(self):
        from .. import utils
        self.doc = utils.IDocument()


class IDocumentUnitTestCase(IDocumentBaseTestCase):

    layer = testing.layers.UnitTestLayer

    def test_serializable(self):
        try:
            self.doc.serialize()
        except NotImplementedError:
            pass
        except AttributeError as err:
            msg = 'Unexpected exception raised: {}'
            self.fail(msg.format(err))


class IDocumentIntegrationTestCase(IDocumentBaseTestCase):

    layer = testing.layers.MongoIntegrationTestLayer
