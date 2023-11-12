from sqlalchemy import insert, select
from typing import Optional, Union
from src.database import task_data, database
import boto3
from botocore.exceptions import ClientError
import json
import os
from dotenv import load_dotenv
from databases.interfaces import Record

async def generatePresignedUrl(bucketName, filePath, file_ext) -> str:
    load_dotenv()
    print("in list_buckets.py")
    print(os.getenv("JWT_SECRET"))
    print("acesskey="+os.getenv("S3_ACCESS_KEY"))
    print(os.getenv("S3_SECRET_KEY"))
    client = boto3.client(
        's3',
        aws_access_key_id=os.getenv("S3_ACCESS_KEY"),
        aws_secret_access_key=os.getenv("S3_SECRET_KEY"),
    )
    if file_ext.lower() == "mov":
        file_ext = "quicktime"
    print("file_ext in generate presigned fn = "+file_ext)    
    presignedUrl = client.generate_presigned_url(
        ClientMethod='put_object', 
        Params={'Bucket':bucketName, 'Key': filePath, 'ContentType' : f'video/{file_ext}'}, 
        ExpiresIn=604800)
    print(presignedUrl)
    return presignedUrl


# generatePresignedUrl("toktik_bucket", "test.txt", "PUT")

async def create_presigned_post(bucket_name, object_name,
                          fields=None, conditions=None, expiration=3600):
    """Generate a presigned URL S3 POST request to upload a file

    :param bucket_name: string
    :param object_name: string
    :param fields: Dictionary of prefilled form fields
    :param conditions: List of conditions to include in the policy
    :param expiration: Time in seconds for the presigned URL to remain valid
    :return: Dictionary with the following keys:
        url: URL to post to
        fields: Dictionary of form fields and values to submit with the POST
    :return: None if error.
    """

    # Generate a presigned S3 POST URL
    s3_client = boto3.client(
        's3',
        aws_access_key_id=os.getenv("S3_ACCESS_KEY"),
        aws_secret_access_key=os.getenv("S3_SECRET_KEY"),
    )
    try:
        response = s3_client.generate_presigned_post(bucket_name,
                                                     object_name,
                                                     Fields=fields,
                                                     Conditions=conditions,
                                                     ExpiresIn=expiration)
    except ClientError as e:
        logging.error(e)
        return None

    # The response contains the presigned URL and required fields
    return response

def generate_s3_file_path(email:str, filename:str) -> str:
    email = email.rsplit('.', 1)[0]
    filepath = email + "/" + filename
    return filepath

async def get_task_by_user_filename(user: str, filename_noext: str) -> Record | None:
    select_query = select(task_data).where(task_data.c.user == user)
    return await database.fetch_one(select_query)