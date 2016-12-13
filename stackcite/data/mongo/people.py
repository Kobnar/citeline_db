import mongoengine

from stackcite.data.json import people

from . import utils


class Name(utils.IEmbeddedDocument):
    """
    A person's full name.
    """

    title = mongoengine.StringField(required=True, unique=True)
    first = mongoengine.StringField()
    middle = mongoengine.StringField()
    last = mongoengine.StringField(required=True)
    _full = mongoengine.StringField(db_field='full', required=True, unique=True)
    prefixes = mongoengine.ListField(mongoengine.StringField(), default=[])
    suffixes = mongoengine.ListField(mongoengine.StringField(), default=[])

    @property
    def full(self):
        """
        A person's full name (e.g. "John Nobody Doe").

        This attribute's setter will attempt to parse a string into a collection
        of first, middle and last names. The getter of this attribute will
        combine all three names into a single string. To that end, the first
        and last words will be considered the first and last names of the
        person. If only one name is provided it will be parsed as a last
        name.

        (This is a required field.)
        """
        prefix = ' '.join([p for p in self.prefixes])
        suffix = ' '.join([s for s in self.suffixes])
        name_chunks = (prefix, self.first, self.middle, self.last, suffix)
        return ' '.join([x for x in name_chunks if x])

    @full.setter
    def full(self, value):
        if not isinstance(value, str):
            msg = '{} is not a string'
            raise TypeError(msg.format(value))

        names = self._parse_name(value)
        self.first = names.get('first')
        self.middle = names.get('middle')
        self.last = names['last']
        self.prefixes = names.get('prefixes')
        self.suffixes = names.get('suffixes')

    @staticmethod
    def _parse_name(name):
        """
        Parses a name string into its individual component parts.

        :param name: A name string
        :return: A 3-tuple (first, middle, last)
        """
        # TODO: Parse prefixes and suffixes.json
        name_chunks = name.split()
        name_dict = dict()

        # extract prefixes and suffixes
        prefixes = list()
        suffixes = list()
        name = list()
        for chunk in name_chunks:
            if chunk in people.PREFIXES:
                prefixes.append(chunk)
            elif chunk in people.SUFFIXES:
                suffixes.append(chunk)
            else:
                name.append(chunk)
        name_dict['prefixes'] = prefixes
        name_dict['suffixes'] = suffixes

        # Parse names
        name_cnt = len(name)
        if name_cnt == 1:
            name_dict['last'] = name[0]
        elif name_cnt == 2:
            name_dict['first'] = name[0]
            name_dict['last'] = name[1]
        else:
            name_dict['first'] = name.pop(0)
            name_dict['last'] = name.pop(-1)
            name_dict['middle'] = ' '.join(name)
        return name_dict

    def clean(self):
        """
        Makes sure both ``title`` and ``full`` have been set and updates value
        for ``full`` to match current combination.
        """
        if self.title and not self.full:
            self.full = self.title
        elif self.full and not self.title:
            self.title = self.full

        self._full = self.full

    def _serialize(self, fields):
        return {
            'title': self.title,
            'first': self.first,
            'middle': self.middle,
            'last': self.last,
            'full': self.full,
            'prefixes': self.prefixes,
            'suffixes': self.suffixes
        }


class Person(utils.IDocument):
    """
    A known person (typically an author, researcher or editor).
    """

    name = mongoengine.EmbeddedDocumentField(Name, required=True, default=Name)
    description = mongoengine.StringField(db_field='desc')
    birth = mongoengine.IntField()
    death = mongoengine.IntField()

    def _serialize(self, fields):
        return {
            'id': str(self.id) if self.id else None,
            'name': self.name.serialize(fields.get('name')),
            'description': self.description,
            'birth': self.birth,
            'death': self.death,
        }
