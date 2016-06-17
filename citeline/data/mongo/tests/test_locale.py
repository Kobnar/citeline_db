import unittest

from citeline import testing


class ISBN10FieldUnitTestCase(unittest.TestCase):

    layer = testing.layers.UnitTestLayer

    def setUp(self):
        from ..locale import ISBN10Field
        self.field = ISBN10Field()

    def test_validate_accepts_valid_isbn10s(self):
        """ISBN10Field.validate() accepts valid ISBN-10 values
        """
        from mongoengine import ValidationError
        for isbn in testing.data.valid_isbn10s():
            try:
                self.field.validate(isbn)
            except ValidationError as err:
                self.fail(err)

    def test_validate_raises_exception_for_invalid_isbns(self):
        """ISBN10Field.validate() raises ValidationError for invalid ISBNs
        """
        from mongoengine import ValidationError
        for isbn in testing.data.invalid_isbns():
            with self.assertRaises(ValidationError):
                self.field.validate(isbn)


class ISBN13FieldUnitTestCase(unittest.TestCase):

    layer = testing.layers.UnitTestLayer

    def setUp(self):
        from ..locale import ISBN13Field
        self.field = ISBN13Field()

    def test_validate_accepts_valid_isbn13s(self):
        """ISBN13Field.validate() accepts valid ISBN-13 values
        """
        from mongoengine import ValidationError
        for isbn in testing.data.valid_isbn13s():
            try:
                self.field.validate(isbn)
            except ValidationError as err:
                self.fail(err)

    def test_validate_raises_exception_for_invalid_isbns(self):
        """ISBN13Field.validate() raises ValidationError for invalid ISBNs
        """
        from mongoengine import ValidationError
        for isbn in testing.data.invalid_isbns():
            with self.assertRaises(ValidationError):
                self.field.validate(isbn)


class PageRangeTestCase(unittest.TestCase):

    layer = testing.layers.UnitTestLayer

    def setUp(self):
        from ..locale import PageRange
        self.range = PageRange()

    def test_pages_accepts_integer(self):
        """PageRange.range accepts a single integer
        """
        start = 12
        try:
            self.range.range = start
        except TypeError as err:
            self.fail(err)

    def test_pages_sets_start_value_with_integer(self):
        """PageRange.range sets a the start value with a single integer
        """
        start = 12
        self.range.range = start
        result = self.range.start
        self.assertEqual(start, result)

    def test_pages_accepts_valid_tuple(self):
        """PageRange.range accepts a valid 2-tuple of values
        """
        pages = 12, 13
        try:
            self.range.range = pages
        except TypeError as err:
            self.fail(err)

    def test_pages_sets_start_value_with_valid_tuple(self):
        """PageRange.range sets a the start value with a single integer
        """
        start = 12
        end = 13
        self.range.range = start, end
        result = self.range.start
        self.assertEqual(start, result)

    def test_pages_sets_end_value_with_valid_tuple(self):
        """PageRange.range sets a the end value with a single integer
        """
        start = 12
        end = 13
        self.range.range = start, end
        result = self.range.end
        self.assertEqual(end, result)

    def test_pages_raises_exception_for_short_tuple(self):
        """PageRange.range raises an exception for a tuple that is too short
        """
        pages = 12,
        with self.assertRaises(ValueError):
            self.range.range = pages

    def test_pages_raises_exception_for_long_tuple(self):
        """PageRange.range raises an exception for a tuple that is too long
        """
        pages = 12, 13, 14
        with self.assertRaises(ValueError):
            self.range.range = pages

    def test_pages_raises_exception_for_non_int_str_or_tuple(self):
        """PageRange.range raises an exception for a non-int or non-tuple
        """
        invalid_vals = [None, 12.5]
        for invalid_val in invalid_vals:
            with self.assertRaises(TypeError):
                self.range.range = invalid_val

    def test_pages_accepts_formatted_string(self):
        """PageRange.range does not raise an exception for a valid string of pages
        """
        valid_pages = (
            'pg. 12',
            'page 12-13',
            '12-13')
        for page in valid_pages:
            try:
                self.range.range = page
            except ValueError as err:
                self.fail(err)

    def test_pages_sets_formatted_strings(self):
        """PageRange.range sets values from a valid string of pages
        """
        # Contains a list of (str, expected) pairs:
        valid_pages = [
            ('pg. 12', (12, None)),
            ('page 12-13', (12, 13)),
            ('12-13', (12, 13))]
        for page_str, expected in valid_pages:
            self.range.range = page_str
            result = self.range.range
            self.assertEqual(expected, result)

    def test_pages_raises_exception_for_invalid_string(self):
        """PageRange.range raises an exception for an invalid string
        """
        invalid_page = "No pages here!"
        with self.assertRaises(ValueError):
            self.range.range = invalid_page

    def test_pages_returns_start_and_end_values(self):
        """PageRange.range returns a 2-tuple of start and end values
        """
        pages = 12, 13
        self.range.start = pages[0]
        self.range.end = pages[1]
        result = self.range.range
        self.assertEqual(pages, result)

    def test_pages_raises_exception_if_start_greater_than_end(self):
        """PageRange.range raises exception if start value is larger than end value
        """
        pages = 14, 13
        with self.assertRaises(ValueError):
            self.range.range = pages

    def test_str_formats_single_value(self):
        """PageRange.__str__() returns a properly formatted "start" value
        """
        start = 12
        expected = 'pg. 12'
        self.range.start = start
        result = str(self.range)
        self.assertEqual(expected, result)

    def test_str_formats_both_values(self):
        """PageRange.__str__() returns properly formatted "start" and "end" values
        """
        start = 12
        end = 13
        expected = 'pg. 12-13'
        self.range.range = start, end
        result = str(self.range)
        self.assertEqual(expected, result)

    def test_serialize_returns_correct_tuple(self):
        """PageRange.serialize() returns a correct tuple of values
        """
        start = 12
        end = 13
        expected = (12, 13)
        self.range.start = start
        self.range.end = end
        result = self.range.serialize()
        self.assertEqual(expected, result)
