#from secretsaws import access_key, secret_access_key
import boto3
import os
# from dotenv import dotenv_values
# config = dotenv_values(".env") 
# access_key=config["access_key"]
# secret_access_key=config["secret_access_key"]
from os import environ
access_key=environ.get("access_key")
secret_access_key=environ.get("secret_access_key")


client = boto3.client('s3', aws_access_key_id = access_key, aws_secret_access_key=secret_access_key)


for file in os.listdir():
	if '.csv' in file:
		upload_file_bucket = 'tpolist-datalake'
		upload_file_key= 'data/' + str(file) + '/' + str(file)
		client.upload_file(file,upload_file_bucket,upload_file_key)