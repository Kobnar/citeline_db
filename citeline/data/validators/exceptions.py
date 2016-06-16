class ValidationError(Exception):
    """
    A custom exception used during aggressive document-level property
    validation.
    """

    def __init__(self, message='', original_error=None):
        self.message = message
        self.original_error = original_error

    def __str__(self):
        return self.message
