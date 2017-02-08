class StackciteError(Exception):
    """
    A custom exception class.
    """

    _DEFAULT_MESSAGE = ''

    def __init__(self, message=None):
        self.message = message or self._DEFAULT_MESSAGE

    def __str__(self):
        if self.message:
            return '{}: {}'.format(self.__class__.__name__, self.message)
        else:
            return self.__class__.__name__
