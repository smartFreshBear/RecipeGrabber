"""
this module contains all the custom exceptions that are used in the project

"""
from werkzeug.exceptions import UnprocessableEntity


class WeCouldNotParseTheResponse(UnprocessableEntity):
    def __init__(self, message: str = None):
        super().__init__(message or 'We could not parse the response')