from starlette import status

from src.constants import ErrorCode


class DetailedError(Exception):
    error_message = None
    error_code = None
    template = None
    status_code = status.HTTP_500_INTERNAL_SERVER_ERROR

    def __init__(self, message=None, template=None):
        self.error_message = message
        self.template = template

    def to_dict(self):
        return {
            "error": {
                "error_code": self.error_code,
                "error_message": self.error_message,
            },
        }


class InvalidInputError(DetailedError):
    error_code = ErrorCode.INVALID_INPUT
    status_code = status.HTTP_400_BAD_REQUEST


class AuthorizationError(DetailedError):
    error_code = ErrorCode.AUTHORIZATION_FAILED
    status_code = status.HTTP_401_UNAUTHORIZED


class NotFoundError(DetailedError):
    error_code = ErrorCode.NOT_FOUND
    status_code = status.HTTP_404_NOT_FOUND


class EmailTakenError(DetailedError):
    error_code = ErrorCode.EMAIL_TAKEN
    status_code = status.HTTP_400_BAD_REQUEST


class AuthRequiredError(DetailedError):
    error_code = ErrorCode.AUTHENTICATION_REQUIRED
    status_code = status.HTTP_307_TEMPORARY_REDIRECT


class InvalidCredentialsError(Exception):
    pass
