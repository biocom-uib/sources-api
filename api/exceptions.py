class ApiException(Exception):
    """Base class for all project exceptions that ensure it all have same format."""

    def __init__(self, code: int, message: str, text=None):
        """Args:
            code: Internal error code.
            message: Short description of the error.
            text: Exception message.
        """
        self._code = code
        self._message = message
        self._text = text
        super().__init__(message)

    @property
    def code(self):
        return self._code

    @property
    def message(self):
        return self._message

    @property
    def text(self):
        return self._text


#  TODO: mesclar amb exceptions aiohttp per tornar códi http correcte
class ClientException(ApiException):
    def __init__(self, code: int, message: str, link: str, status_code: int, text=None):
        """Args:
            code: Internal error code.
            message: Short description of the error.
            link: Link to detailed error description
            status_code: Http response code
            text: Exception message.
        """
        self._status_code = status_code
        self._link = link
        super().__init__(code, message, text=text)

    @property
    def status_code(self):
        return self._status_code

    @property
    def link(self):
        return self._link


# TODO: mesclar amb exceptions aiohttp per tornar códi http correcte
class ServerException(ApiException):
    def __init__(self, code=0, message=None, text=None):
        super().__init__(code, message, text=text)


class BadRequestException(ClientException):
    HTTP_BAD_REQUEST = 400

    def __init__(self, code: int, message: str, link: str, text=None):
        super().__init__(code, message, link, self.HTTP_BAD_REQUEST, text=text)
