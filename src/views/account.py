import fastapi
from fastapi import BackgroundTasks, Depends, Form
from pydantic import ValidationError
from starlette import status
from starlette.requests import Request
from starlette.responses import HTMLResponse, RedirectResponse
from starlette.templating import Jinja2Templates

from src.dependencies import get_templates, get_user_id_from_cookie
from src.exceptions import (
    AuthorizationError,
    AuthRequiredError,
    EmailTakenError,
    InvalidCredentialsError,
    InvalidInputError,
    NotFoundError,
)
from src.models.schema import AccountPageView, LoginForm, RegisterForm, User
from src.services import user_service
from src.settings import cookie_settings
from src.utils.cookie_auth import get_auth_cookies_settings

router = fastapi.APIRouter()
templates: Jinja2Templates = get_templates()


@router.get("/account/me", include_in_schema=False)
async def get_account(
        request: Request,
        user_id: int = Depends(get_user_id_from_cookie),
):
    if not user_id:
        raise AuthRequiredError("Unauthorized access!")
    view_account = AccountPageView(user_id=user_id)
    try:
        view_account.user = await user_service.get_user_by_id(user_id)
    except ValidationError as er:
        error = er.errors()[0]
        raise NotFoundError(error["msg"]) from er
    return templates.TemplateResponse(
        request=request, name="account/index.html", context=view_account.model_dump()
    )


@router.get("/register", include_in_schema=False)
async def get_register(
        request: Request,
):
    return templates.TemplateResponse(request=request, name="auth/register.html")


@router.post("/register", response_class=HTMLResponse)
async def post_register_user(
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
async def get_login(
        request: Request,
):
    return templates.TemplateResponse(request=request, name="auth/login.html")


@router.post("/login", response_class=HTMLResponse)
async def post_auth_user(
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
        user_account = await user_service.authenticate_user(email, password)
    except InvalidCredentialsError as er:
        raise AuthorizationError(er, template="auth/login.html") from er

    user = User(**user_account)
    worker.add_task(user_service.update_user_login_at, user.id)

    response = RedirectResponse("/account/me", status_code=status.HTTP_302_FOUND)
    response.set_cookie(**get_auth_cookies_settings(user.id))
    return response


@router.get("/account/logout", response_class=RedirectResponse, include_in_schema=False)
async def get_logout():
    response = RedirectResponse(url="/", status_code=status.HTTP_302_FOUND)
    response.delete_cookie(cookie_settings.NAME_COOKIES)
    return response
