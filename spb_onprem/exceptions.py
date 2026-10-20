

class BaseSDKError(Exception):
    pass


class SDKConfigError(BaseSDKError):
    pass


class BadParameterError(BaseSDKError):
    pass


class NotFoundError(BaseSDKError):
    pass


class RequestError(BaseSDKError):
    pass


class BadRequestError(RequestError):
    pass


class BadRequestParameterError(BadRequestError):
    pass


class ResponseError(BaseSDKError):
    pass


class BadResponseError(ResponseError):
    pass


class UnknownError(BaseSDKError):
    pass


class BadDeletionTargetError(BadParameterError, ValueError):
    """The targets of a deletion are missing, ambiguous or empty.

    It is a ValueError too, so either can be caught.
    """
    pass


class GraphQLError(UnknownError):
    """A GraphQL error from the platform, with its code and details.

    It is an UnknownError, so code that catches UnknownError keeps working.

    Attributes:
        code (Optional[str]): The error code (``code``, else ``extensions.code``).
        details (dict): The error details the platform sent (``details``), or {}.
        errors (list): All GraphQL errors of the response.
    """

    def __init__(self, message: str, code=None, details=None, errors=None):
        super().__init__(message)
        self.code = code
        self.details = details or {}
        self.errors = errors or []


class InvalidInputError(GraphQLError):
    """BAD_REQUEST: the platform refused the input (for example invalid VLM settings)."""


class ForbiddenError(GraphQLError):
    """FORBIDDEN: the caller may not do this."""


class ConflictError(GraphQLError):
    """CONFLICT: the target changed or is busy.

    For VLM settings it means they changed since they were read
    (``expected_updated_at`` did not match); read them again and retry.
    ``details`` has ``expectedUpdatedAt`` and ``currentUpdatedAt``.
    """
