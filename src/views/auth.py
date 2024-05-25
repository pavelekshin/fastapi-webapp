from fastapi import APIRouter, BackgroundTasks, Form
from pydantic import ValidationError
from starlette import status
from starlette.requests import Request
from starlette.responses import HTMLResponse, RedirectResponse
from starlette.templating import Jinja2Templates

from src.dependencies import get_templates
from src.exceptions import (
    AuthorizationError,
    EmailTakenError,
    InvalidCredentialsError,
    InvalidInputError,
)
from src.models.schema import LoginForm, RegisterForm, User
from src.services import user_service
from src.utils.cookie_auth import get_auth_cookies_settings

router = APIRouter()
templates: Jinja2Templates = get_templates()


@router.get("/register", include_in_schema=False)
async def get_register_form(
        request: Request,
):
    return templates.TemplateResponse(request=request, name="auth/register.html")


@router.post("/register", response_class=HTMLResponse)
async def post_register_form(
        name: str = Form(),
        email: str = Form(),
        password: str = Form(),
        age: int = Form(),
):
    try:
        register_form = RegisterForm(name=name, email=email, password=password, age=age)
    except ValidationError as er:
        error = er.errors()[0]
        raise InvalidInputError(error["msg"], template="auth/register.html") from er
    if await user_service.get_user_by_email(register_form.email):
        raise EmailTakenError(
            "Account with this email already exists", template="auth/register.html"
        )
    user_account = await user_service.create_account(register_form)
    user = User(**user_account)
    response = RedirectResponse(url="/account/me", status_code=status.HTTP_302_FOUND)
    response.set_cookie(**get_auth_cookies_settings(user.id))

    return response


@router.get("/login", response_class=HTMLResponse)
async def get_login_form(
        request: Request,
):
    return templates.TemplateResponse(request=request, name="auth/login.html")


@router.post("/login", response_class=HTMLResponse)
async def post_login_form(
        worker: BackgroundTasks,
        email: str = Form(),
        password: str = Form(),
):
    try:
        LoginForm(email=email, password=password)
    except ValidationError as er:
        error = er.errors()[0]
        raise InvalidInputError(error["msg"], template="auth/login.html") from er

    try:
        user = User(**await user_service.authenticate_user(email, password))
    except InvalidCredentialsError as er:
        raise AuthorizationError(er, template="auth/login.html") from er

    worker.add_task(user_service.update_user_login_at, user.id)

    response = RedirectResponse("/account/me", status_code=status.HTTP_302_FOUND)
    response.set_cookie(**get_auth_cookies_settings(user.id))
    return response
