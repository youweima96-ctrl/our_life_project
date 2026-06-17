from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api import conflicts, events, reports, rooms
from app.core.config import get_settings


settings = get_settings()
app = FastAPI(title=settings.app_name)

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


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}

