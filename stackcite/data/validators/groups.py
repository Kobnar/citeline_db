from stackcite.data.json import auth

from . import exceptions


def validate_group(group):
    """
    Validates a given group. Returns the initial ``group`` string if
    the group is good and ``None`` if the group fails validation.

    :param str group: A group name string.
    """
    if group in auth.GROUPS:
        return group


class GroupValidator(object):
    """
    A `mongoengine` style group validator. Raises :class:`.ValidationError`
    if the group provided is invalid.
    """
    def __init__(self, msg=None):
        if msg is None:
            self.msg = 'Invalid group: {}'
        else:
            self.msg = msg

    def __call__(self, group):
        if not (isinstance(group, str) and validate_group(group)):
            raise exceptions.ValidationError(self.msg.format(group))
