import unittest

from stackcite.data import testing


class NameBaseTestCase(unittest.TestCase):

    def setUp(self):
        from ..people import Name
        self.name = Name()


class NameUnitTestCase(NameBaseTestCase):

    layer = testing.layers.UnitTestLayer

    def test_title_does_not_change_last_name(self):
        """Name.title does not set a new last name
        """
        self.name.title = 'Jenson'
        self.assertFalse(self.name.full)

    def test_two_part_title_does_not_change_first_name(self):
        """Name.title does not set a new first name
        """
        self.name.title = 'Jenson'
        self.assertFalse(self.name.full)

    def test_three_part_title_does_not_change_middle_name(self):
        """Name.title does not set a new middle name
        """
        self.name.title = 'Joe N. Doe'
        self.assertFalse(self.name.full)

    def test_last_required(self):
        """Name.last is a required field
        """
        self.name.first = 'John'
        self.name.middle = 'Nobody'
        from mongoengine import ValidationError
        with self.assertRaises(ValidationError):
            self.name.validate()

    def test_full_is_string(self):
        """Name.full is a string
        """
        self.name.first = 'John'
        self.name.middle = 'Nobody'
        self.name.last = 'Doe'
        self.assertIsInstance(self.name.full, str)

    def test_full_combines_all_names(self):
        """Name.full combines all names into one string
        """
        self.name.first = 'John'
        self.name.middle = 'Nobody'
        self.name.last = 'Doe'
        expected = 'John Nobody Doe'
        self.assertEqual(self.name.full, expected)

    def test_full_combines_first_and_last_without_middle_names(self):
        """Name.full combines first and last names if no middle name provided
        """
        self.name.first = 'John'
        self.name.last = 'Doe'
        expected = 'John Doe'
        self.assertEqual(self.name.full, expected)

    def test_full_last_name_only_if_only_name(self):
        """Name.full only displays the last name if it is the only name available
        """
        self.name.last = 'Doe'
        expected = 'Doe'
        self.assertEqual(self.name.full, expected)

    def test_full_setter_raises_exception_if_not_string(self):
        """Name.full setter raises `TypeError` if `value` is not a string
        """
        bad_types = [None, True, False, 123, 1.23]
        for typ in bad_types:
            with self.assertRaises(TypeError):
                self.name.full = typ

    def test_full_setter_parses_last_name_with_full_name(self):
        """Name.full setter parses a last name if a full name is given
        """
        name = 'John Nobody Doe'
        self.name.full = name
        self.assertEqual(self.name.last, 'Doe')

    def test_full_setter_parses_first_name_with_full_name(self):
        """Name.full setter parses a first name if a full name is given
        """
        name = 'John Nobody Doe'
        self.name.full = name
        self.assertEqual(self.name.first, 'John')

    def test_full_setter_parses_middle_name_with_full_name(self):
        """Name.full setter parses a middle name if a full name is given
        """
        name = 'John Nobody Doe'
        self.name.full = name
        self.assertEqual(self.name.middle, 'Nobody')

    def test_full_setter_parses_last_name_with_partial_name(self):
        """Name.full setter parses a last name if only first and last name are given
        """
        name = 'John Doe'
        self.name.full = name
        self.assertEqual(self.name.last, 'Doe')

    def test_full_setter_parses_first_name_with_partial_name(self):
        """Name.full setter parses a first name if only first and last name are given
        """
        name = 'John Doe'
        self.name.full = name
        self.assertEqual(self.name.first, 'John')

    def test_full_setter_assums_single_name_is_last_name(self):
        """Name.full setter assumes a single name is a last name
        """
        name = 'Doe'
        self.name.full = name
        self.assertEqual(self.name.last, 'Doe')

    def test_full_setter_assumes_extra_names_are_middle_names(self):
        """Name.full setter assumes any extra names are middle names
        """
        name = 'John Nobody Unknown Forever Doe'
        self.name.full = name
        self.assertEqual(self.name.middle, 'Nobody Unknown Forever')

    def test_full_setter_catches_known_prefixes(self):
        """Name.full setter catches known prefixes
        """
        from ..people import Name
        name = 'John Nobody Doe'
        prefixes = ['Dr.', 'Mr.', 'Ms.', 'Mrs.', 'Miss', 'Sir']
        for prefix in prefixes:
            case = ' '.join([prefix, name])
            name_obj = Name()
            name_obj.full = case
            expected = [prefix]
            result = name_obj.serialize()['prefixes']
            self.assertEqual(expected, result)

    def test_full_setter_catches_known_suffixes(self):
        """Name.full setter catches known suffixes.json
        """
        from ..people import Name
        name = 'John Nobody Doe'
        suffixes = ['Jr.', 'Sr.', 'I', 'II', 'IV', 'V']
        for suffix in suffixes:
            case = ' '.join([name, suffix])
            name_obj = Name()
            name_obj.full = case
            expected = [suffix]
            result = name_obj.serialize()['suffixes']
            self.assertEqual(expected, result)

    def test_full_setter_catches_multiple_known_prefixes(self):
        """Name.full setter catches multiple known prefixes
        """
        name = 'Sir Dr. John Nobody Doe'
        self.name.full = name
        expected = ['Sir', 'Dr.']
        result = self.name.prefixes
        self.assertEqual(expected, result)

    def test_full_setter_catches_multiple_known_suffixes(self):
        """Name.full setter catches multiple known suffixes
        """
        name = 'John Nobody Doe Esq. III'
        self.name.full = name
        expected = ['Esq.', 'III']
        result = self.name.suffixes
        self.assertEqual(expected, result)

    def test_full_setter_does_not_set_title(self):
        """Name.full does not set a new title
        """
        self.name.full = 'John Nobody Doe'
        self.assertIsNone(self.name.title)

    def test_serialize_formats_correctly(self):
        """Name.serialize() method returns a properly formatted dictionary
        """
        from ..people import Name
        for p in testing.data.people():
            expected = p['name']
            name = Name()
            name.title = expected['title']
            name.full = expected['full']
            result = name.serialize()
            self.assertEqual(expected, result)

    def test_serialize_formats_sparse_fields_correctly(self):
        """Name.serialize() method returns a properly formatted dictionary with sparse values
        """
        self.name.last = 'Doe'
        expected = {
            'title': None,
            'first': None,
            'middle': None,
            'last': 'Doe',
            'full': 'Doe',
            'prefixes': [],
            'suffixes': []
        }
        result = self.name.serialize()
        self.assertEqual(expected, result)

    def test_serialize_filters_fields(self):
        """Name.serialize() filters explicitly named fields
        """
        fields = ('title', 'first', 'last')
        self.name.title = 'J.N. Doe'
        self.name.full = 'John Nobody Doe'
        self.name.clean()
        expected = {
            'title': 'J.N. Doe',
            'first': 'John',
            'last': 'Doe'
        }
        result = self.name.serialize(fields)
        self.assertEqual(expected, result)

    def test_clean_sets_full_as_title_if_full_not_set(self):
        """Name.clean() sets full name as title if full has not been set
        """
        full_name = 'John Nobody Doe'
        self.name.full = full_name
        self.name.clean()
        self.assertEqual(self.name.title, full_name)

    def test_clean_sets_title_as_full_if_title_not_set(self):
        """Name.clean() sets title name as full if title has not been set
        """
        title = 'J.N. Doe'
        self.name.title = title
        self.name.clean()
        self.assertEqual(self.name.title, title)

    def test_prefixes_default_empty_list(self):
        """Name.prefixes defaults to an empty list
        """
        self.assertEqual([], self.name.prefixes)

    def test_suffixes_default_empty_list(self):
        """Name.suffixes defaults to an empty list
        """
        self.assertEqual([], self.name.suffixes)


class PersonBaseTestCase(unittest.TestCase):

    def setUp(self):
        from ..people import Person
        self.person = Person()

    def tearDown(self):
        self.person = None


class PersonUnitTestCase(PersonBaseTestCase):

    layer = testing.layers.UnitTestLayer

    def test_name_default_is_a_name(self):
        """Person.name defaults to a Name
        """
        from ..people import Name
        self.assertIsInstance(self.person.name, Name)

    def test_name_default_is_an_empty_name(self):
        """Person.name defaults to an empty Name
        """
        self.assertEqual(self.person.name.first, None)
        self.assertEqual(self.person.name.middle, None)
        self.assertEqual(self.person.name.last, None)

    def test_name_is_required(self):
        """Person.name is a required field (Name.last must be set)
        """
        from mongoengine import ValidationError
        with self.assertRaises(ValidationError):
            self.person.validate()

    def test_serialize_formats_correctly(self):
        """Person.serialize() returns a properly formatted nested dictionary
        """
        people = testing.data.people()
        from ..people import Person
        from bson import ObjectId
        for p in people:
            p['id'] = str(ObjectId())
            person = Person()
            person.id = p['id']
            person.name.title = p['name']['title']
            person.name.full = p['name']['full']
            person.description = p['description']
            person.birth = p['birth']
            person.death = p['death']
            result = person.serialize()
            self.assertEqual(p, result)

    def test_serialize_deserialize_sparse_fields_correctly(self):
        """Person.serialize() handles sparse fields
        """
        from bson import ObjectId
        person_dict = {
            'id': str(ObjectId()),
            'name': {
                'title': 'John Doe',
                'first': 'John',
                'middle': None,
                'last': 'Doe',
                'full': 'John Doe',
                'prefixes': [],
                'suffixes': []
            },
            'description': 'Nobody knows who he is.',
            'birth': None,
            'death': None
        }
        self.person.id = person_dict['id']
        self.person.name.title = person_dict['name']['title']
        self.person.name.full = person_dict['name']['full']
        self.person.description = person_dict['description']
        self.person.birth = person_dict['birth']
        self.person.death = person_dict['death']
        result = self.person.serialize()
        self.assertEqual(person_dict, result)

    def test_serialize_filters_fields(self):
        """Person.serialize() filters explicitly named fields
        """
        from bson import ObjectId
        person_dict = {
            'id': str(ObjectId()),
            'name': {
                'title': 'John Doe',
                'first': 'John',
                'middle': None,
                'last': 'Doe',
                'full': 'John Doe',
            },
            'description': 'Nobody knows who he is.',
            'birth': None,
            'death': None
        }
        self.person.id = person_dict['id']
        self.person.name.title = person_dict['name']['title']
        self.person.name.full = person_dict['name']['full']
        self.person.description = person_dict['description']
        self.person.birth = person_dict['birth']
        self.person.death = person_dict['death']
        expected = {
            'name': {'full': 'John Doe'},
            'description': 'Nobody knows who he is.'
        }
        fields = ('description', 'name.full')
        result = self.person.serialize(fields)
        self.assertEqual(expected, result)

    def test_deserialize_works(self):
        """Person.deserialize() correctly populates serialized data
        """
        people = testing.data.people()
        from ..people import Person
        for p in people:
            person = Person()
            person.deserialize(p)
            self.assertEqual(person.id, None)
            self.assertEqual(person.name.first, p['name']['first'])
            self.assertEqual(person.name.middle, p['name']['middle'])
            self.assertEqual(person.name.last, p['name']['last'])
            self.assertEqual(person.description, p['description'])
            self.assertEqual(person.birth, p['birth'])
            self.assertEqual(person.death, p['death'])


class PersonIntegrationTestCase(PersonBaseTestCase):

    layer = testing.layers.MongoIntegrationTestLayer

    def setUp(self):
        from ..people import Person
        Person.drop_collection()
        super().setUp()

    def test_title_must_be_unique(self):
        """Person.name.full must be a unique field
        """
        from mongoengine import NotUniqueError
        from ..people import Person
        full_name = 'John Nobody Doe'
        title = 'J.N. Doe'
        self.person.name.full = full_name
        self.person.name.title = title
        self.person.save()
        dup_person = Person()
        dup_person.name.full = 'Other Name'
        dup_person.name.title = title
        with self.assertRaises(NotUniqueError):
            dup_person.save()

    def test_full_name_must_be_unique(self):
        """Person.name.full must be a unique field
        """
        from mongoengine import NotUniqueError
        from ..people import Person
        full_name = 'John Nobody Doe'
        title = 'J.N. Doe'
        self.person.name.full = full_name
        self.person.name.title = title
        self.person.save()
        dup_person = Person()
        dup_person.name.full = full_name
        dup_person.name.title = 'Other Title'
        with self.assertRaises(NotUniqueError):
            dup_person.save()
