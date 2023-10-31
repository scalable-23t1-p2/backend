import logging
import boto3
from botocore.exceptions import ClientError
import os
from typing import Dict
from src.s3 import list_buckets as s3_list_buckets

"""
In boto3, the client and resource are two different ways to interact with AWS services.

The client provides a low-level interface to AWS services. It allows you to make direct API calls to AWS services and 
returns the raw response from the service. The client is useful when you need fine-grained control over the API calls and want to optimize performance.

On the other hand, the resource provides a higher-level object-oriented interface to AWS services. 
It abstracts away many of the low-level details of the API calls and provides a more Pythonic interface. 
The resource is useful when you want to work with AWS resources as Python objects and don't need fine-grained control over the API calls.
"""
client = boto3.client('s3')
s3 = boto3.resource('s3')

# with open('filename', 'rb') as data:
#     s3.upload_fileobj(data, 'mybucket', 'mykey')

async def upload_raw(save_as: any, filebytes: any) -> Dict[str, str]:
    bucket_name = "toktikbucket"
    bucket_list = await s3_list_buckets.list_buckets()
    
    try:
        print("uploading")
        found = bucket_name in bucket_list["buckets"]
        if not found:
            client.create_bucket(bucket_name)
        else:
            print("Bucket {0} already exists".format(bucket_name))
            result = client.put_object(
                Bucket=bucket_name,
                Key=save_as+".mp4",
                Body=filebytes,
            )
        return {"message": "File uploaded successfully Uploaded!"}

    except Exception as e:
        return {"error": str(e)}
