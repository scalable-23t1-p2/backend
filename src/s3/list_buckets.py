import asyncio
import logging
import boto3
from botocore.exceptions import ClientError
import json
import os
from dotenv import load_dotenv

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
# client = boto3.client('s3')
# s3 = boto3.resource('s3')

async def list_buckets():
    try:
        response = client.list_buckets()
        bucket_list = []
        for bucket in response['Buckets']:
            bucket_list.append(bucket["Name"])
        return {"buckets": json.dumps(bucket_list)}
    except ClientError as e:
        logging.error(e)
        return {"error": str(e)}
