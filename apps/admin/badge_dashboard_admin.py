from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

router = APIRouter()
templates = Jinja2Templates(directory="apps/admin/templates")

@router.get("/admin/badges", response_class=HTMLResponse)
async def badge_dashboard(request: Request):
    return templates.TemplateResponse("badge_admin.html", {
        "request": request,
        "title": "Badge Analytics – LocalLift Admin"
    })
