import boto3
import pandas as pd
import io
import re
import time
#from secretsaws import access_key, secret_access_key
from dotenv import dotenv_values
config = dotenv_values(".env") 
access_key=config["access_key"]
secret_access_key=config["secret_access_key"]

params = {
    'region': 'us-east-1',
    'database': 'dojodatabase',
    'bucket': 'tpolist-transformed',
    'path': 'script',
    'query': 'SELECT * FROM customers limit 10'
}

session = boto3.Session()

def athena_query(client, params):
    
    response = client.start_query_execution(
        QueryString=params["query"],
        QueryExecutionContext={
            'Database': params['database']
        },
        ResultConfiguration={
            'OutputLocation': 's3://' + params['bucket'] + '/' + params['path']
        }
    )
    return response

def athena_to_s3(session, params, max_execution = 5):
    client = session.client('athena', region_name=params["region"], aws_access_key_id = access_key, aws_secret_access_key=secret_access_key)
    execution = athena_query(client, params)
    execution_id = execution['QueryExecutionId']
    state = 'RUNNING'

    while (max_execution > 0 and state in ['RUNNING', 'QUEUED']):
        max_execution = max_execution - 1
        response = client.get_query_execution(QueryExecutionId = execution_id)

        if 'QueryExecution' in response and \
                'Status' in response['QueryExecution'] and \
                'State' in response['QueryExecution']['Status']:
            state = response['QueryExecution']['Status']['State']
            if state == 'FAILED':
                return False
            elif state == 'SUCCEEDED':
                s3_path = response['QueryExecution']['ResultConfiguration']['OutputLocation']
                filename = re.findall('.*\/(.*)', s3_path)[0]
                return filename
        time.sleep(1)
    
    return False

def s3_to_pandas(session, params, s3_filename):    
    s3client = session.client('s3',aws_access_key_id = access_key, aws_secret_access_key=secret_access_key)
    obj = s3client.get_object(Bucket=params['bucket'],
                              Key=params['path'] + '/' + s3_filename)
    df = pd.read_csv(io.BytesIO(obj['Body'].read()))
    return df


def traer_df(myquery):
    # Query Athena and get the s3 filename as a result
    params.update({'query': myquery})
    s3_filename = athena_to_s3(session, params)
    mydf=s3_to_pandas(session, params, s3_filename)
    cleanup(session, params)
    return mydf

# Deletes all files in your path so use carefully!
def cleanup(session, params):
    s3 = session.resource('s3',aws_access_key_id = access_key, aws_secret_access_key=secret_access_key)
    my_bucket = s3.Bucket(params['bucket'])
    for item in my_bucket.objects.filter(Prefix=params['path']):
        item.delete()
    


