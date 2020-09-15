from google.cloud import storage        # pip install google-cloud-storage
import os
import json

os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = 'credentials.json'


def list_blobs(bucket_name):
    """Lists all the blobs in the bucket."""
    storage_client = storage.Client()

    # Note: Client.list_blobs requires at least package version 1.17.0.
    blobs = storage_client.list_blobs(bucket_name)

    return blobs


def upload_file(source_file, destination_file, bucket):
    blob = bucket.blob(destination_file)
    blob.upload_from_filename(filename=source_file)


def upload_dict_as_json(data, destination_file, bucket):
    # will migrate to gcs_file_handle.py
    blob = bucket.blob(destination_file)
    blob.upload_from_string(json.dumps(data))


def download_json_as_dict(source_file, bucket):
    # will migrate to gcs_file_handle.py
    content = bucket.get_blob(source_file).download_as_string()
    return json.loads(content)


def main():
    bucket_name = '<bucket name>'
    gcs_source_file = '<file name in GCS>'
    gcs_destination_file = '<file name in GCS>'
    local_source_file = '<path to data>.json'
    dict_test = dict({"aaa": "bbb", "ccc": 123})

    client = storage.Client()
    bucket = client.bucket(bucket_name)

    # ファイルをアップロードする
    upload_file(source_file=local_source_file, destination_file=gcs_destination_file, bucket=bucket)

    # Dictをアップロードする
    upload_dict_as_json(dict_test, destination_file=gcs_destination_file, bucket=bucket)

    # DataFrameにダウンロードする
    # JsonファイルをDictにダウンロードする
    dct = download_json_as_dict(gcs_source_file, bucket)
    print(dct)


if __name__ == '__main__':
    main()
