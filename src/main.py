from fastapi import FastAPI

from s3.router import router as s3_router

app = FastAPI()

@app.get("/")
async def root():
    return {"message": "Hello World"}

# app.include_router(auth_router, prefix="/auth", tags=["Auth"])
app.include_router(s3_router, prefix="/s3", tags=["S3"])