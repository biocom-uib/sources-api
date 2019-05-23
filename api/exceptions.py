from aiohttp import web
import json


class ErrorCodes:
    UNKNOWN = 1
    BAD_KEY = 2
    TYPE_ERROR = 3
    MISSING_PARAMETER = 4


# do not raise or inherit directly, assume it also extends some HTTPException
class ApiException(Exception):
    """Base class for all project exceptions that ensure it all have same format."""

    def __init__(self, code, message, description=None):
        """Args:
            code: Internal error code.
            message: Short description of the error.
            text: Exception message.
        """
        self._code = code
        self._message = message
        self._description = description
        super().__init__(message)

    @property
    def code(self):
        return self._code

    @property
    def message(self):
        return self._message

    @property
    def description(self):
        return self._description


class ServerException(ApiException):
    def __init__(self, code, message, description=None):
        super().__init__(code, message, description=description)


class ClientException(ApiException):
    def __init__(self, code, message, description=None):
        """Args:
            code: Internal error code.
            message: Short description of the error.
            link: Link to detailed error description
            status_code: Http response code
            text: Exception message.
        """
        super().__init__(code, message, description=description)


class BadRequestException(ClientException):
    def __init__(self, code, message, description=None):
        super().__init__(code, message, description=description)


def raise_http_error(cls, code, message, description=None, reason=None, headers=None, **kwargs):
    if issubclass(cls, web.HTTPServerError):
        if len(kwargs) > 0:
            raise_http_error(web.HTTPInternalServerError, 0, 'unused arguments in raise_http_error: ' + str(list(kwargs.keys())))

        class CustomException(cls, ServerException):
            def __init__(self):
                cls.__init__(self, headers=headers, reason=reason, text=None, content_type='application/json')
                ServerException.__init__(self, code=code, message=message, description=description)

        raise CustomException()

    elif issubclass(cls, web.HTTPClientError):
        if cls == web.HTTPMethodNotAllowed:
            if set(kwargs.keys()) != {'method', 'allowed_methods'}:
                raise_http_error(web.HTTPInternalServerError, 0,
                    'invalid arguments for HTTPMethodNotAllowed in raise_http_error: ' + str(list(kwargs.keys())))

            class CustomException(cls, ClientException):
                def __init__(self):
                    cls.__init__(self, kwargs['method'], kwargs['allowed_methods'], headers=headers, reason=reason, text=None, content_type='application/json')
                    ClientException.__init__(self, code=code, message=message, description=description)

            raise CustomException()

        else:
            if len(kwargs) > 0:
                raise_http_error(web.HTTPInternalServerError, 0, 'unused arguments in raise_http_error: ' + str(list(kwargs.keys())))

            api_cls = BadRequestException if cls == web.HTTPBadRequest else ClientException

            class CustomException(cls, api_cls):
                def __init__(self):
                    cls.__init__(self, headers=headers, reason=reason, text=None, content_type='application/json')
                    api_cls.__init__(self, code=code, message=message, description=description)

            raise CustomException()

    else:
        raise_http_error(web.HTTPInternalServerError, 0, 'invalid HTTP error class: ' + cls.__name__)


def raise_bad_request(code, message, description=None, reason=None, headers=None):
    raise_http_error(web.HTTPBadRequest, code, message, description=description, reason=reason, headers=headers)


def ensure_key_as(cls, key, dic):
    if key not in dic:
        raise_bad_request(ErrorCodes.MISSING_PARAMETER, f"missing field \"{key}\"")

    val = dic[key]

    if not isinstance(val, cls):
        raise_bad_request(ErrorCodes.TYPE_ERROR, f"{key} should be of type {cls.__name__}")

    return val


def ensure_list_of(cls, key, dic):
    if key not in dic:
        raise_bad_request(ErrorCodes.MISSING_PARAMETER, f"missing field \"{key}\"")

    xs = dic[key]

    if not isinstance(xs, list) or not all(isinstance(x, cls) for x in xs):
        raise_bad_request(ErrorCodes.TYPE_ERROR, f"{key} should be a list of {cls.__name__}")

    return xs

