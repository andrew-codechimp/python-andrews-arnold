"""Asynchronous Python client for AndrewsArnold."""


class AndrewsArnoldError(Exception):
    """Generic exception."""


class AndrewsArnoldConnectionError(AndrewsArnoldError):
    """AndrewsArnold connection exception."""


class AndrewsArnoldAuthenticationError(AndrewsArnoldError):
    """AndrewsArnold authentication exception."""


class AndrewsArnoldValidationError(AndrewsArnoldError):
    """AndrewsArnold validation exception."""


class AndrewsArnoldNotFoundError(AndrewsArnoldError):
    """AndrewsArnold not found exception."""


class AndrewsArnoldBadRequestError(AndrewsArnoldError):
    """AndrewsArnold bad request exception."""
