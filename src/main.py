from fastapi import FastAPI
from src.database import database
from src.s3.router import router as s3_router
from src.auth.router import router as auth_router
from starlette.middleware.cors import CORSMiddleware
from src.config import app_configs, settings
import aioredis

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_origin_regex=settings.CORS_ORIGINS_REGEX,
    allow_credentials=True,
    allow_methods=("GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"),
    allow_headers=settings.CORS_HEADERS,
)

# if settings.ENVIRONMENT.is_deployed:
#     sentry_sdk.init(
#         dsn=settings.SENTRY_DSN,
#         environment=settings.ENVIRONMENT,
#     )


@app.on_event("startup")
async def startup() -> None:
    await database.connect()


@app.get("/")
async def root():
    return {"message": "Hello World"}

# @app.on_event("startup")
# async def startup() -> None:
#     await database.connect()


# @app.on_event("shutdown")
# async def shutdown() -> None:
#     await database.disconnect()

app.include_router(auth_router, prefix="/auth", tags=["Auth"])
app.include_router(s3_router, prefix="/s3", tags=["S3"])