from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .config import settings
from .api.v1.router import api_router

app = FastAPI(
    title="Bugninja Platform API",
    description="Backend API for the Bugninja Platform",
    version="0.1.0",
    debug=settings.DEBUG,
)

# Set up CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API router
app.include_router(api_router, prefix="/api/v1")


@app.get("/")
async def root():
    return {"message": "Bugninja Platform API", "version": "0.1.0"}


@app.get("/health")
async def health_check():
    return {"status": "healthy"}
