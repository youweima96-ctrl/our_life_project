from pathlib import Path

from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware

from app.api import conflicts, events, reports, rooms
from app.core.config import get_settings


settings = get_settings()
app = FastAPI(title=settings.app_name)
web_dir = Path(__file__).resolve().parent / "web"

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(events.router, prefix=settings.api_prefix)
app.include_router(rooms.router, prefix=settings.api_prefix)
app.include_router(conflicts.router, prefix=settings.api_prefix)
app.include_router(reports.router, prefix=settings.api_prefix)

app.mount("/web", StaticFiles(directory=web_dir), name="web")


@app.get("/", include_in_schema=False)
def web_index() -> FileResponse:
    return FileResponse(web_dir / "index.html")


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}
