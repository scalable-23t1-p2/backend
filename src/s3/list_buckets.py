import asyncio
import logging
import boto3
from botocore.exceptions import ClientError
import json

client = boto3.client('s3')
s3 = boto3.resource('s3')

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
