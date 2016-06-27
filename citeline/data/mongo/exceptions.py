from citeline.base import exceptions as exc


class AuthenticationError(exc.CiteLineError):
    """
    A custom exception raised when authentication fails for whatever reason.
    """

    _DEFAULT_MESSAGE = 'Authentication failed'
