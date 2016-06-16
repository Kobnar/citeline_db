import unittest

from citeline import testing


class YearBaseTestCase(unittest.TestCase):

    def setUp(self):
        from ..locale import Year
        self.year = Year()


class YearUnitTestCase(YearBaseTestCase):

    layer = testing.layers.UnitTestLayer

    def tearDown(self):
        self.year = None

    def test_full_is_read_only(self):
        """Year.full is read-only
        """
        with self.assertRaises(AttributeError):
            self.year.full = 1999

    def test_returns_string_with_ace_if_value_positive(self):
        """Year.full returns a string (e.g. `1999`)
        """
        self.year.value = 1999
        self.assertEqual(self.year.full, '1999 A.C.E.')

    def test_returns_string_with_bce_if_value_negative(self):
        """Year.full returns a string (e.g. `1999`)
        """
        self.year.value = -400
        self.assertEqual(self.year.full, '400 B.C.E.')

    def test_serialize_returns_int(self):
        """Year.serialize() returns an integer representing its value
        """
        expected = 1999
        self.year.value = expected
        result = self.year.serialize()
        self.assertEqual(expected, result)

    def test_deserialize_sets_value(self):
        """Year.deserialize() sets value"""
        expected = 1999
        self.year.deserialize(expected)
        self.assertEqual(expected, self.year.value)


class ISBNBaseTestCase(unittest.TestCase):

    def setUp(self):
        from ..locale import ISBN
        self.isbn = ISBN()


class ISBNUnitTestCase(ISBNBaseTestCase):

    layer = testing.layers.UnitTestLayer

    def tearDown(self):
        self.isbn = None

    def test_set_get_isbn10(self):
        """ISBN.isbn() can get/set an ISBN-10
        """
        from citeline.testing import data
        isbn_10s = data.valid_isbn10s()
        for isbn in isbn_10s:
            expected = isbn.replace('-', '')
            self.isbn.set_isbn(isbn)
            self.assertEqual(self.isbn.isbn10, expected)

    def test_set_isbn10_sets_isbn13(self):
        """ISBN.isbn() also sets an ISBN-13 if given an ISBN-10
        """
        from citeline.testing import data
        isbn_10s = data.valid_isbn10s()
        isbn_13s = data.valid_isbn13s()
        for idx, isbn in enumerate(isbn_10s):
            expected = isbn_13s[idx].replace('-', '')
            self.isbn.set_isbn(isbn)
            self.assertEqual(self.isbn.isbn13, expected)

    def test_set_get_isbn13(self):
        """ISBN.isbn() can get/set an ISBN-13
        """
        from citeline.testing import data
        isbn_13s = data.valid_isbn13s()
        for isbn in isbn_13s:
            expected = isbn.replace('-', '')
            self.isbn.set_isbn(isbn)
            self.assertEqual(self.isbn.isbn13, expected)

    def test_set_isbn13_sets_isbn10(self):
        """ISBN.isbn() also sets an ISBN-10 if given an ISBN-13
        """
        from citeline.testing import data
        isbn_10s = data.valid_isbn10s()
        isbn_13s = data.valid_isbn13s()
        for idx, isbn in enumerate(isbn_13s):
            expected = isbn_10s[idx].replace('-', '')
            self.isbn.set_isbn(isbn)
            self.assertEqual(self.isbn.isbn10, expected)

    def test_isbn_sets_none_value(self):
        self.isbn.set_isbn('9780985339890')
        self.isbn.set_isbn(None)
        self.assertIsNone(self.isbn.isbn10)
        self.assertIsNone(self.isbn.isbn13)

    def test_isbn_raises_exception_with_bad_ISBN(self):
        """ISBN.isbn() raises an exception for an invalid ISBN
        """
        from citeline.data import validators
        with self.assertRaises(validators.ValidationError):
            self.isbn.set_isbn('bad_isbn')

    def test_serialize_returns_isbns_if_set(self):
        """ISBN.serialize() returns a pair of ISBNs if they have been set
        """
        isbn13 = '9780985339890'
        isbn10 = '0985339896'
        self.isbn.set_isbn(isbn13)
        expected = {
            'isbn13': isbn13,
            'isbn10': isbn10}
        result = self.isbn.serialize()
        self.assertEqual(expected, result)

    def test_deserialize_sets_isbns(self):
        """ISBN.deserialize() sets a pair of ISBNs
        """
        isbn13 = '9780985339890'
        isbn10 = '0985339896'
        data = {
            'isbn13': isbn13,
            'isbn10': isbn10}
        self.isbn.deserialize(data)
        self.assertEqual(self.isbn.isbn13, isbn13)
        self.assertEqual(self.isbn.isbn10, isbn10)
