from contextlib import asynccontextmanager
from typing import AsyncGenerator

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse
from fastapi.staticfiles import StaticFiles

from app.api.v1.router import api_router
from app.config import settings
from dev.delete_all_data import delete_all_data
from dev.upload_realistic_data import setup_content_folders, upload_realistic_data


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    # TODO! REENABLE THESE!!!
    delete_all_data(force=True)
    setup_content_folders()
    upload_realistic_data()

    yield


app = FastAPI(
    title="Bugninja Platform API",
    description="Backend API for the Bugninja Platform",
    version="0.1.0",
    debug=settings.DEBUG,
    lifespan=lifespan,
)


@app.get("/", include_in_schema=False)
async def redirect() -> RedirectResponse:
    return RedirectResponse(url="/docs")


# Set up CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files for content access
app.mount("/content", StaticFiles(directory="content"), name="content")
app.mount("/screenshots", StaticFiles(directory="screenshots"), name="screenshots")

# Include API router
app.include_router(api_router, prefix="/api/v1")
