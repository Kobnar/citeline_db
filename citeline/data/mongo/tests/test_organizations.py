import unittest

from citeline import testing


class OrganizationBaseTestLayer(unittest.TestCase):

    def setUp(self):
        from ..organizations import Organization
        self.org = Organization()


class OrganizationUnitTestLayer(OrganizationBaseTestLayer):

    layer = testing.layers.UnitTestLayer

    def test_name_is_required(self):
        """Organization.name is a required field
        """
        from ..organizations import Organization
        org = Organization()
        from mongoengine import ValidationError
        with self.assertRaises(ValidationError):
            org.validate()

    def test_serialize_formats_correctly(self):
        """Organization.serialize() returns a correct dict
        """
        org_name = 'South Sea Company'
        org_est = 1720
        self.org.name = org_name
        self.org.established = org_est
        expected = {
            'id': None,
            'name': org_name,
            'established': org_est}
        result = self.org.serialize()
        self.assertEqual(expected, result)

    def test_deserialize_sets_correct_values(self):
        """Organization.deserialize() sets correct values
        """
        name = 'South Sea Company'
        est = 1720
        data = {
            'name': name,
            'established': est}
        self.org.deserialize(data)
        self.assertEqual(name, self.org.name)
        self.assertEqual(est, self.org.established)


class OrganizationIntegrationTestLayer(OrganizationBaseTestLayer):

    layer = testing.layers.MongoIntegrationTestLayer

    def setUp(self):
        from ..organizations import Organization
        Organization.drop_collection()
        super().setUp()

    def test_name_is_unique(self):
        """Organization.name is unique
        """
        from ..organizations import Organization
        name = 'Organization'
        org_1 = Organization()
        org_2 = Organization()
        org_1.name = name
        org_2.name = name
        org_1.save()
        from mongoengine import NotUniqueError
        with self.assertRaises(NotUniqueError):
            org_2.save()


class PublisherBaseTestLayer(unittest.TestCase):

    def setUp(self):
        from ..organizations import Publisher
        self.publisher = Publisher()


class PublisherUnitTestLayer(PublisherBaseTestLayer):

    layer = testing.layers.UnitTestLayer

    def test_serialize_returns_region(self):
        """Publisher.serialize() returns dict containing correct region data
        """
        name = 'Random House'
        est = 1922
        region = 'US'
        self.publisher.name = name
        self.publisher.established = est
        self.publisher.region = region
        expected = {
            'id': None,
            'name': name,
            'established': est,
            'region': region}
        result = self.publisher.serialize()
        self.assertEqual(expected, result)
