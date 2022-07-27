import boto3
from os import environ
#from secretsaws import access_key, secret_access_key
# from dotenv import dotenv_values
# config = dotenv_values(".env") 
# access_key=config["access_key"]
# secret_access_key=config["secret_access_key"]
access_key=environ.get("access_key")
secret_access_key=environ.get("secret_access_key")


s3 = boto3.resource(
  's3',
  region_name='us-east-1',
  aws_access_key_id=access_key,
  aws_secret_access_key=secret_access_key
)

BUCKET_NAME = 'tpolist-datalake'
BUCKET_FILE_NAME = 'geolocation.csv'
LOCAL_FILE_NAME = 'downloaded.csv'

def download_s3_file():
    # s3=boto3.client('s3', aws_access_key_id = access_key, aws_secret_access_key=secret_access_key)
    s3.download_file(BUCKET_NAME, BUCKET_FILE_NAME,LOCAL_FILE_NAME)



