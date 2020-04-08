from google.cloud import storage        # pip install google-cloud-storage
import os
import re
from io import StringIO
import pandas as pd
import pyarrow as pa
import pyarrow.parquet as pq

os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = 'credentials.json'


def list_blobs(bucket_name):
    """Lists all the blobs in the bucket."""
    storage_client = storage.Client()

    # Note: Client.list_blobs requires at least package version 1.17.0.
    blobs = storage_client.list_blobs(bucket_name)

    return blobs


def upload_file(source_file, destination_file, bucket, content_type='application/vnd.ms-excel'):
    blob = bucket.blob(destination_file)
    blob.upload_from_filename(filename=source_file, content_type=content_type)


def upload_dataframe(df, destination_file, bucket, index=False, content_type='application/vnd.ms-excel'):
    blob = bucket.blob(destination_file)

    if content_type in ['csv', 'application/vnd.ms-excel']:
        bytes_to_write = df.to_csv(None, index=index).encode()
        blob.upload_from_string(bytes_to_write, content_type=content_type)
    elif content_type in ['parquet']:
        # pyarrowのTableに変換
        table = pa.Table.from_pandas(df)

        # Bufferにテーブルを書き込み
        buf = pa.BufferOutputStream()
        pq.write_table(table, buf, compression=None)

        blob.upload_from_string(data=buf.getvalue().to_pybytes())
    else:
        print('invalid content_type selected')


def download_dataframe(source_file, bucket, encodings, skip_rows=0, line_feed_code='\n'):
    for encoding in encodings:
        try:
            content = bucket.get_blob(source_file).download_as_string().decode(encoding)
            lines = re.split(line_feed_code, content)

            buff = list()
            for i, line in enumerate(lines):
                if i >= skip_rows:
                    buff.append(line)
            content = '{}'.format(line_feed_code).join(buff)

            df = pd.read_csv(StringIO(content))

            return df
        except Exception as e:
            print(e)
            continue
    return pd.DataFrame()


def main():
    bucket_name = '<bucket name>'
    gcs_source_file = '<file name in GCS>'
    gcs_destination_file = '<file name in GCS>'
    local_source_file = '<path to data>.csv'

    client = storage.Client()
    bucket = client.bucket(bucket_name)

    # ファイルをアップロードする
    upload_file(source_file=local_source_file, destination_file=gcs_destination_file, bucket=bucket,
                content_type='application/vnd.ms-excel')

    # DataFrameをアップロードする
    df = pd.DataFrame()
    upload_dataframe(df, destination_file=gcs_destination_file, bucket=bucket, content_type='application/vnd.ms-excel')

    # DataFrameにダウンロードする
    df = download_dataframe(source_file=gcs_source_file, bucket=bucket, encodings=['utf8'])
    print(df)


if __name__ == '__main__':
    main()
