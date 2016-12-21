import os
import hashlib
import mongoengine


def gen_key():
    """
    Generates a cryptographic key used for API Tokens and account confirmation.
    """
    return hashlib.sha224(os.urandom(128)).hexdigest()


class ISerializable(object):
    """
    An interface providing methods required to serialze a document.
    """

    def _serialize(self, fields):
        """
        Provides a completely serialized version of a document.

        :param fields: A pre-processed field registry from :func:`~parse_fields`
        :return: A serialized representation of :class:`~Person`
        """
        raise NotImplementedError()

    def serialize(self, fields=None):
        """
        Filters :property:`~serialized` against a list of dot-notation formatted
        field names (e.g. ``'author.name.first'``).

        :param fields: A list of dot-notation formatted field names
        :return: A serialized representation of the object
        """
        # TODO: Auto-dereference flag
        fields = self.parse_fields(fields)
        data = self._serialize(fields)
        if fields:
            return {k: v for k, v in data.items() if k in fields}
        else:
            return data

    @staticmethod
    def parse_fields(fields):
        """
        Parses a list of field name strings into a field registry (a nested
        dictionary of field names and sub-fields) to help serialize values.

        Example:
        ```
        parse_fields(['author.name.first', 'author.name.last', 'description'])
        # Output:
        # {
        #     'author': {
        #         'name': {
        #             'first': {}
        #             'last': {}
        #         }
        #     'description': {}
        # }
        ```

        :param fields: A list or tuple of dot-notation formatted field names
        :return: A nested multi-dict with field names as its keys
        """

        def _append_tokens(tokens, registry):
            """
            Recursively appends tokens to an existing field registry by using the
            first token in each iteration as a key and creating new keys when no
            existing key is found.
            """
            key = tokens.pop(0)
            try:
                sub_registry = registry[key]
            except KeyError:
                registry[key] = sub_registry = {}
            if tokens:
                _append_tokens(tokens, sub_registry)

        if not fields:
            return {}
        else:
            if isinstance(fields, dict):
                return fields
            else:
                output = {}
                for field in fields:
                    field = field.split('.')
                    _append_tokens(field, output)
                return output


class IDeserializable(object):
    """
    An interface providing the methods to deserialize an object.
    """

    def _deserialize(self, data):
        for key, value in data.items():
            try:
                getattr(self, key).deserialize(value)
            except AttributeError:
                setattr(self, key, value)

    def deserialize(self, data):
        """
        Deserializes a nested dictionary of values into a Python object. Can
        also be used to update an existing document with new data.

        :param data: A nested dictionary of values
        """
        self._deserialize(data)


class IEmbeddedDocument(mongoengine.EmbeddedDocument,
                        ISerializable, IDeserializable):
    """
    A common interface for all embedded documents.
    """

    meta = {'abstract': True}


class IDocument(mongoengine.Document,
                ISerializable, IDeserializable):
    """
    A common interface for all documents.
    """

    meta = {'abstract': True}
