

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