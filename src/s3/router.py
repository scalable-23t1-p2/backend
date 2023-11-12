import ast
from io import BytesIO

from databases.interfaces import Record
from fastapi import APIRouter, Depends, File, Form, UploadFile
from pydantic import EmailStr
from src.auth.dependencies import valid_refresh_token
from src.auth.jwt import parse_jwt_user_data
from src.auth.schemas import JWTData
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
from src.database import task_data, database
from src.s3 import service as s3_service
from src.auth import service
from celery.result import AsyncResult

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

# @router.post("/ex1")
# def run_task(data=Body(...)):
#     print(data)
#     amount = int(data["amount"])
#     x = data["x"]
#     y = data["y"]
#     task = create_task(add.delay(x, y))
#     return JSONResponse()

@router.post("/upload_link", status_code=status.HTTP_201_CREATED)
async def upload(
    filename: str = Form(...),
    refresh_token: Record = Depends(valid_refresh_token),
    jwt_data: JWTData = Depends(parse_jwt_user_data),
) -> dict[str, str]:
    user = await service.get_user_by_uuid(jwt_data.user_id)
    user_email: str = user["email"]
    file_ext = filename.rsplit('.', 1)[1]
    filepath = s3_service.generate_s3_file_path(user_email, filename)
    presigned_url = await s3_service.generatePresignedUrl("toktikbucket", filepath.strip(),file_ext.strip())
    return {"presigned_url": presigned_url}


@router.post("/process_vid", status_code=status.HTTP_201_CREATED)
async def process_vid(
    filename: str = Form(...),
    jwt_data: JWTData = Depends(parse_jwt_user_data),
)-> dict[str, str]:
    user = await service.get_user_by_uuid(jwt_data.user_id)
    user_email: str = user["email"]
    s3_filepath = s3_service.generate_s3_file_path(user_email, filename)
    filename_noext = filename.rsplit('.', 1)[0]
    print("hello inside process_vid"+user_email)
    # result = celery_app.send_task('thumbnail', args=[param])
    task = celery_app.send_task('convert', queue='q01', args=[filename,s3_filepath])
    res = AsyncResult(task.task_id)
    print("this tuple task ="+str(res.result))
    # task2 = celery_app.send_task('thumbnail', queue='q02', args=[param])
    # new = task_result(task_id=task.task_id, task_type="thumbnail")
    insert_query = (
        insert(task_data)
        .values(
            {
                "task_id": task.task_id,
                "task_type": 'convert',
                "user": user_email,
                "filename_noext": filename_noext,
            }
        )
    )
    await database.fetch_one(insert_query)
    # result = await task.get()
    # print("all task result ="+result) 
    # print(f'inside_process_vid:{result}')
    return {"return_value": "success"}



@router.post("/track_upload", status_code=status.HTTP_201_CREATED)
async def track_upload(
    filename: str = Form(...),
    jwt_data: JWTData = Depends(parse_jwt_user_data),
)-> dict[str, str]:
    user = await service.get_user_by_uuid(jwt_data.user_id)
    user_email: str = user["email"]
    filename_noext = filename.rsplit('.', 1)[0]
    print("hello inside track upload of "+user_email+' filename='+filename)
    select_query = select(task_data).where(task_data.c.user == user_email and task_data.c.filename_noext == filename_noext)
    db_res: Record = await database.fetch_one(select_query)
    print("db_res = "+str(db_res))
    print(db_res["task_id"]) #return task id for convert_task
    convert_result = AsyncResult(db_res["task_id"]).state
    res = AsyncResult(db_res["task_id"])  #return task id for convert_task
    print("this tuple task ="+str(res.result))
    (chunk_tid, thumbnail_tid) = res.result #return task id for chunk_task and thumbnail_task
    
    #check if chunk task is in the tasl_data table or not
    select_query_chunk = select(task_data).where(task_data.c.task_id == chunk_tid)
    db_chunk_res: Record = await database.fetch_one(select_query_chunk)
    if db_chunk_res is None:
        insert_query = (
            insert(task_data)
            .values(
                {
                    "task_id": chunk_tid,
                    "task_type": 'chunk',
                    "user": user_email,
                    "filename_noext": filename_noext,
                }
            )
        )
        await database.fetch_one(insert_query)

    #check if thumbnail task is in the tasl_data table or not
    select_query_thumbnail = select(task_data).where(task_data.c.task_id == thumbnail_tid)
    db_thumbnail_res: Record = await database.fetch_one(select_query_thumbnail)
    if db_thumbnail_res is None:
        insert_query = (
            insert(task_data)
            .values(
                {
                    "task_id": thumbnail_tid,
                    "task_type": 'thumbnail',
                    "user": user_email,
                    "filename_noext": filename_noext,
                }
            )
        )
        await database.fetch_one(insert_query)

    print("chunk_tid = "+str(chunk_tid)) 
    print("thumbnail_tid = "+str(thumbnail_tid))
    chunk_result = AsyncResult(chunk_tid).state
    print("chunk_result = "+str(chunk_result))
    thumbnail_result = AsyncResult(thumbnail_tid).state
    print("thumbnail_result = "+str(thumbnail_result))
    if thumbnail_result == 'SUCCESS' and chunk_result == 'SUCCESS' and convert_result == 'SUCCESS':
        return {"return_value": "100%"}
    elif convert_result == "SUCCESS" and thumbnail_result == 'SUCCESS' and chunk_result != 'SUCCESS':
        return {"return_value": "50%"}
    elif {convert_result == "SUCCESS" and thumbnail_result != 'SUCCESS' and chunk_result != 'SUCCESS'}:
        return {"return_value": "25%"}
    else:   
        return {"return_value": "0%"}
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
