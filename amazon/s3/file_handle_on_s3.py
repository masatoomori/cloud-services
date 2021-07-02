import os
import io
import re
import json

import pandas as pd
import boto3

CRED_PATHS = [os.curdir]
CRED_FILE = '<file name>'

BUCKET = '<bucket name>'
BUCKET_KEY = '<path to file in a bucket>'
FILE_NAME = '<file name>'


def load_aws_cred(cred_file):
    for p in CRED_PATHS:
        f = os.path.join(p, cred_file)
        if os.path.exists(f):
            contents = open(f, 'r').readlines()
            contents = [c.strip() for c in contents]
            content = dict(zip(re.split(',', contents[0]), re.split(',', contents[1])))
            return content
    return None


def read_df_from_s3(bucket, key, cred, encoding='utf8', dtype=object, delimiter=','):
    access_key = cred['Access key ID']
    access_secret = cred['Secret access key']
    client = boto3.client('s3', aws_access_key_id=access_key, aws_secret_access_key=access_secret)
    obj = client.get_object(Bucket=bucket, Key=key)
    df = pd.read_csv(io.BytesIO(obj['Body'].read()), encoding=encoding, dtype=dtype, delimiter=delimiter)

    return df


def write_df_to_s3(df, bucket, key, cred, sep=','):
    access_key = cred['Access key ID']
    access_secret = cred['Secret access key']
    client = boto3.client('s3', aws_access_key_id=access_key, aws_secret_access_key=access_secret)
    bytes_to_write = df.to_csv(None, sep=sep, index=False).encode()
    response = client.put_object(Bucket=bucket, Key=key, Body=bytes_to_write)

    return response


def load_json_from_s3(bucket, key, cred):
    access_key = cred['Access key ID']
    access_secret = cred['Secret access key']
    s3 = boto3.resource('s3', aws_access_key_id=access_key, aws_secret_access_key=access_secret)

    content_object = s3.Object(bucket, key)
    file_content = content_object.get()['Body'].read()
    json_content = json.loads(file_content)

    return json_content


def find_files_in_s3(bucket, cred, prefix=None, suffix=None, full_path=False):
    access_key = cred['Access key ID']
    access_secret = cred['Secret access key']
    client = boto3.client('s3', aws_access_key_id=access_key, aws_secret_access_key=access_secret)

    if prefix is None:
        response = client.list_objects_v2(Bucket=bucket)
    else:
        response = client.list_objects_v2(Bucket=bucket, Prefix=prefix)

    files = [content['Key'] for content in response['Contents']]

    if suffix is not None:
        files = [f for f in files if f.endswith(suffix)]

    if not full_path:
        files = [re.split('/', f)[-1] for f in files]
        files = [f for f in files if f != '']

    return files


def write_matrix_to_s3(matrix, bucket, key, delimiter=','):
    """
    matrix = [[1, 2, 3],
              [4, 5, 6],
              [7, 8, 9]]
    """
    matrix = [delimiter.join([str(i) for i in line]) for line in matrix]

    s3 = boto3.resource('s3')
    obj = s3.Object(bucket, key)
    response = obj.put(Body='\n'.join(matrix))

    return response


def test():
    cred = load_aws_cred(CRED_FILE)
    df_data = pd.DataFrame()
    write_df_to_s3(df_data, BUCKET, FILE_NAME, cred)


if __name__ == '__main__':
    test()
