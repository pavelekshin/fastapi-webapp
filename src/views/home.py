import fastapi
from fastapi import Depends
from starlette.requests import Request
from starlette.responses import HTMLResponse
from starlette.templating import Jinja2Templates

from src.dependencies import get_templates, get_user_id_from_cookie
from src.models.schema import HomePageView, Package, ViewModelBase
from src.services import aggr_service, package_service

router = fastapi.APIRouter()
templates: Jinja2Templates = get_templates()


@router.get("/", response_class=HTMLResponse, include_in_schema=False)
async def index(
    request: Request,
    user_id: int = Depends(get_user_id_from_cookie),
):
    stats_counts = await aggr_service.get_count_statistics()
    home_page_view = HomePageView(user_id=user_id, **stats_counts)
    home_page_view.packages = [
        Package(**p) for p in await package_service.latest_packages(limit=7)
    ]
    return templates.TemplateResponse(
        request=request,
        name="home/index.html",
        context=home_page_view.model_dump(),
    )


@router.get("/about", response_class=HTMLResponse, include_in_schema=False)
async def about(
    request: Request,
    user_id: int = Depends(get_user_id_from_cookie),
):
    view_base = ViewModelBase(user_id=user_id)
    return templates.TemplateResponse(
        request=request,
        name="home/about.html",
        context=view_base.model_dump(),
    )
