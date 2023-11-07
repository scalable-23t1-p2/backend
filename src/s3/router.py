import ast
from io import BytesIO

# from databases.interfaces import Record
from fastapi import APIRouter, Depends, File, Form, UploadFile
from pydantic import EmailStr
from starlette import status

# from src.auth import service
# from src.auth.dependencies import valid_refresh_token
# from src.auth.jwt import parse_jwt_user_data
# from src.auth.schemas import JWTData
# from s3 import objects_list
import os
from dotenv import load_dotenv
from celery import Celery
from sqlalchemy import insert, select
from src.s3 import list_buckets as s3_list_buckets
from src.s3 import upload_raw as s3_upload_raw
from src.database import task_result, database

router = APIRouter()
BROKER_URL = os.getenv("CELERY_BROKER_URL")
RESULT_BACKEND = os.getenv("CELERY_RESULT_BACKEND")
celery_app = Celery('thumbnail', broker=BROKER_URL,
                    backend=RESULT_BACKEND)

@router.get("/hello", status_code=status.HTTP_200_OK)
async def say_hi():
    return {"message": "Hello World S3"}

@router.get("/list_bucket", status_code=status.HTTP_200_OK)
async def list_buckets():
    bucket_list = await s3_list_buckets.list_buckets()
    return bucket_list

@router.post("/upload_raw", status_code=status.HTTP_201_CREATED)
async def upload_raw(
    file: UploadFile = File(...),
    name: str = Form(...),
)-> dict[str, str]:
    file_contents = await file.read()
    file_bytes = BytesIO(file_contents)
    upload_raw_result = await s3_upload_raw.upload_raw(name, file_bytes)
    return upload_raw_result

@router.get("/process_vid", status_code=status.HTTP_200_OK)
async def process_vid()-> dict[str, str]:
    param = "test"
    print("hello inside process_vid")
    # result = celery_app.send_task('thumbnail', args=[param])
    task0 = celery_app.send_task('convert', queue='q01')
    task = celery_app.send_task('thumbnail', queue='q02', args=[param])
    # new = task_result(task_id=task.task_id, task_type="thumbnail")
    insert_query = (
        insert(task_result)
        .values(
            {
                "task_id": task.task_id,
                "task_type": 'thumbnail',
            }
        )
    )
    await database.fetch_one(insert_query)
    # print(f'inside_process_vid:{result}')
    return {"return_value": "success"}


# @router.post("/ex1")
# def run_task(data=Body(...)):
#     print(data)
#     amount = int(data["amount"])
#     x = data["x"]
#     y = data["y"]
#     task = create_task(add.delay(x, y))
#     return JSONResponse()

# @router.post("/upload", status_code=status.HTTP_201_CREATED)
# async def upload(
#     refresh_token: Record = Depends(valid_refresh_token),
#     file: UploadFile = File(...),
#     name: str = Form(...),
#     jwt_data: JWTData = Depends(parse_jwt_user_data),
# ) -> dict[str, str]:
#     user = await service.get_user_by_id(jwt_data.user_id)
#     file_contents = await file.read()
#     file_bytes = BytesIO(file_contents)
#     email: EmailStr = user["email"]
#     upload_result = await s3upload.upload_file(email, name, file_bytes)
#     return upload_result


# @router.get("/list", status_code=status.HTTP_200_OK)
# async def list_files(
#     refresh_token: Record = Depends(valid_refresh_token),
#     jwt_data: JWTData = Depends(parse_jwt_user_data),
# ):
#     user = await service.get_user_by_id(jwt_data.user_id)
#     email: EmailStr = user["email"]
#     file_lists = await objects_list.list_objects(email)
#     literal = ast.literal_eval(file_lists)
#     return literal
