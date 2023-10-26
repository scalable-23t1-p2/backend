from fastapi import FastAPI
from database import database
from s3.router import router as s3_router
from auth.router import router as auth_router

app = FastAPI()

@app.get("/")
async def root():
    return {"message": "Hello World"}

@app.on_event("startup")
async def startup() -> None:
    await database.connect()


@app.on_event("shutdown")
async def shutdown() -> None:
    await database.disconnect()

app.include_router(auth_router, prefix="/auth", tags=["Auth"])
app.include_router(s3_router, prefix="/s3", tags=["S3"])