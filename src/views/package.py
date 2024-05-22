import fastapi
from fastapi import BackgroundTasks, Depends
from starlette.requests import Request
from starlette.responses import HTMLResponse
from starlette.templating import Jinja2Templates

from src.dependencies import (
    get_package_from_cache,
    get_templates,
    get_user_id_from_cookie,
)
from src.models.schema import DetailPackageView
from src.redis import RedisData, set_redis_key
from src.services import aggr_service

router = fastapi.APIRouter()
templates: Jinja2Templates = get_templates()


@router.get("/project/{package_name}", response_class=HTMLResponse)
async def get_package_details(
        worker: BackgroundTasks,
        request: Request,
        package_name: str,
        user_id: int = Depends(get_user_id_from_cookie),
        package_cache: str = Depends(get_package_from_cache),
):
    if not package_cache:
        package_details = await aggr_service.get_package_details(package_name)
        view_details = DetailPackageView(user_id=user_id, **package_details)
        redis_data = RedisData(
            key="package_" + package_name.strip(),
            value=view_details.model_dump_json(exclude={"user_id", "is_logged_in"}),
            ttl=60,
        )
        worker.add_task(set_redis_key, redis_data)
    else:
        view_details = DetailPackageView.model_validate_json(package_cache)
        view_details.user_id = user_id
    if not view_details.package:
        return templates.TemplateResponse(
            request=request,
            name="error/error.html",
            context={
                "context": f"{package_name} not found",
            },
        )
    return templates.TemplateResponse(
        request=request,
        name="packages/packages.html",
        context=view_details.model_dump(),
    )
