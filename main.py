from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.routes import router
from backend.schemas import HealthResponse
from backend.settings import get_settings


settings = get_settings()


app = FastAPI(
    title="LegalEase API",
    description=(
        "AI-powered legal document drafting backend."
    ),
    version="1.0.0",
)


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.include_router(router)


@app.get(
    "/",
    response_model=HealthResponse
)
def root():

    return HealthResponse(
        status="ok",
        message="API is running",
        service=settings.app_name
    )


@app.get(
    "/health",
    response_model=HealthResponse
)
def health():

    return HealthResponse(
        status="healthy",
        message="Service is healthy",
        service=settings.app_name
    )