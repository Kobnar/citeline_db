class AuthenticationError(Exception):
    """
    A custom exception raised when authentication fails for whatever reason.
    """

    _DEFAULT_MESSAGE = 'Authentication failed'

    def __init__(self, message=None):
        self.message = message or self._DEFAULT_MESSAGE

    def __str__(self):
        return self.message
