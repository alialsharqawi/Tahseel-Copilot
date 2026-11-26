import os

from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse

from api.v1 import router as api_v1_router
from core.config import AuthConfigurationError

app = FastAPI(title=os.getenv("TAHSEEL_APP_TITLE", "Tahseel API"))


@app.exception_handler(AuthConfigurationError)
def handle_auth_configuration_error(
    _request: Request, _exc: AuthConfigurationError
) -> JSONResponse:
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"detail": "Application configuration is invalid or incomplete."},
    )


app.include_router(api_v1_router)


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}
