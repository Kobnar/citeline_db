from stackcite.base import exceptions as exc


class ValidationError(exc.StackciteError):
    """
    A custom exception raised when data fails validation.
    """

    _DEFAULT_MESSAGE = 'Validation failed'

    def __init__(self, message='', original_error=None):
        super().__init__(message)
        self.original_error = original_error
