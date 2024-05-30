from fastapi import FastAPI, HTTPException
from starlette.requests import Request
from starlette.responses import RedirectResponse, Response

from src.dependencies import get_templates
from src.exceptions import (
    AuthorizationError,
    AuthRequiredError,
    EmailTakenError,
    InvalidInputError,
    NotFoundError,
)

templates = get_templates()


async def invalid_input_exception_handler(
        request: Request,
        exception: [InvalidInputError | AuthorizationError | EmailTakenError],
) -> Response:
    return templates.TemplateResponse(
        request=request,
        name=exception.template,
        status_code=exception.status_code,
        context=exception.to_dict(),
    )


async def invalid_request_exception_handler(
        request: Request, exception: [NotFoundError]
) -> Response:
    return templates.TemplateResponse(
        request=request,
        name="error/error.html",
        status_code=exception.status_code,
        context=exception.to_dict(),
    )


async def auth_required_exception_handler(
        request: Request, exception: [AuthRequiredError]
) -> Response:
    return RedirectResponse(url="/login", status_code=exception.status_code)


async def not_found_404_exception_handler(request: Request, exception: [HTTPException]):
    return templates.TemplateResponse(
        request=request,
        name="error/error.html",
        status_code=exception.status_code,
    )


def register_error_handlers(app: FastAPI) -> None:
    app.add_exception_handler(InvalidInputError, invalid_input_exception_handler)
    app.add_exception_handler(AuthorizationError, invalid_input_exception_handler)
    app.add_exception_handler(EmailTakenError, invalid_input_exception_handler)
    app.add_exception_handler(NotFoundError, invalid_request_exception_handler)
    app.add_exception_handler(AuthRequiredError, auth_required_exception_handler)
    app.add_exception_handler(404, not_found_404_exception_handler)
