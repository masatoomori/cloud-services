from google.cloud import storage        # pip install google-cloud-storage
import os
from io import StringIO
import pandas as pd

os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = '<service account defined in GCP>.json'
BUCKET_NAME = '<bucket name>'
FILE_NAME = '<file name in GCS>'

DATA_FILE = '<path to data>.csv'


def list_blobs(bucket_name):
    """Lists all the blobs in the bucket."""
    storage_client = storage.Client()

    # Note: Client.list_blobs requires at least package version 1.17.0.
    blobs = storage_client.list_blobs(bucket_name)

    return blobs


def upload_file(source_file, destination_file, bucket, content_type='application/vnd.ms-excel'):
    blob = bucket.blob(destination_file)
    blob.upload_from_filename(filename=source_file, content_type=content_type)


def upload_dataframe(df, destination_file, bucket, content_type='application/vnd.ms-excel'):
    blob = bucket.blob(destination_file)
    bytes_to_write = df.to_csv(None, index=False).encode()
    blob.upload_from_string(bytes_to_write, content_type=content_type)


def download_dataframe(source_file, bucket, encoding='utf8'):
    content = bucket.get_blob(source_file).download_as_string().decode(encoding)
    df = pd.read_csv(StringIO(content))

    return df


def main():
    client = storage.Client()
    bucket = client.bucket(BUCKET_NAME)

    # ファイルをアップロードする
    upload_file(source_file=DATA_FILE, destination_file=FILE_NAME, bucket=bucket,
                content_type='application/vnd.ms-excel')

    # DataFrameをアップロードする
    df = pd.DataFrame()
    upload_dataframe(df, destination_file=FILE_NAME, bucket=bucket, content_type='application/vnd.ms-excel')

    # DataFrameにダウンロードする
    df = download_dataframe(source_file=FILE_NAME, bucket=bucket, encoding='utf8')
    print(df)


if __name__ == '__main__':
    main()
