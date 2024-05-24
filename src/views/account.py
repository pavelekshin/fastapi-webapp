import fastapi
from fastapi import Depends
from pydantic import ValidationError
from starlette import status
from starlette.requests import Request
from starlette.responses import RedirectResponse
from starlette.templating import Jinja2Templates

from src.dependencies import get_templates, get_user_id_from_cookie
from src.exceptions import (
    AuthRequiredError,
    NotFoundError,
)
from src.models.schema import AccountPageView, User
from src.services import user_service
from src.settings import cookie_settings

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
        view_account.user = User(**await user_service.get_user_by_id(user_id))
    except ValidationError as er:
        error = er.errors()[0]
        raise NotFoundError(error["msg"]) from er
    return templates.TemplateResponse(
        request=request, name="account/index.html", context=view_account.model_dump()
    )


@router.get("/account/logout", response_class=RedirectResponse, include_in_schema=False)
async def get_logout():
    response = RedirectResponse(url="/", status_code=status.HTTP_302_FOUND)
    response.delete_cookie(cookie_settings.NAME_COOKIES)
    return response
