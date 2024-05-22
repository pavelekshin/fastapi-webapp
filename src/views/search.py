import fastapi
from fastapi import BackgroundTasks, Depends, Query
from starlette.requests import Request
from starlette.responses import HTMLResponse
from starlette.templating import Jinja2Templates

from src.dependencies import (
    get_search_from_cache,
    get_templates,
    get_user_id_from_cookie,
)
from src.exceptions import NotFoundError
from src.models.schema import SearchPageView, Package
from src.redis import RedisData, set_redis_key
from src.services.package_service import search_packages_by_id

router = fastapi.APIRouter()
templates: Jinja2Templates = get_templates()


@router.get("/search/", response_class=HTMLResponse)
async def search(
        worker: BackgroundTasks,
        request: Request,
        q: str | None = Query(),
        user_id: int = Depends(get_user_id_from_cookie),
        search_cache: str = Depends(get_search_from_cache),
):
    page_view = SearchPageView(user_id=user_id)
    if not q:
        raise NotFoundError(template="search/search.html")
    if not search_cache:
        page_view.packages = [Package(**p) for p in await search_packages_by_id(q)]
        redis_data = RedisData(
            key="search_" + q.strip(),
            value=page_view.model_dump_json(exclude={"user_id", "is_logged_in"}),
            ttl=60,
        )
        worker.add_task(set_redis_key, redis_data)
    else:
        page_view.model_validate_json(search_cache)
        page_view.user_id = user_id
    return templates.TemplateResponse(
        request=request,
        name="search/search.html",
        context=page_view.model_dump(),
    )
