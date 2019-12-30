from google.cloud import bigquery       # pip install google-cloud-bigquery
from google.cloud import storage        # pip install google-cloud-storage
import os

os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = '<service account defined in GCP>.json'
SOURCE_BUCKET_NAME = '<bucket name>'

BQ_DATASET_NAME = '<dataset name>'
TABLE_ID = '<table name>'

SCHEMA = [
    bigquery.SchemaField('<column 0>', 'INTEGER'),
    bigquery.SchemaField('<column 1>', 'DATE'),
    bigquery.SchemaField('<column 2>', 'STRING')
]


def list_blobs(bucket_name):
    """Lists all the blobs in the bucket."""
    storage_client = storage.Client()

    # Note: Client.list_blobs requires at least package version 1.17.0.
    blobs = storage_client.list_blobs(bucket_name)

    return blobs


def insert_values(client, dataset_ref, table_id, schema, source_uris, n_skip_rows=1):
    job_config = bigquery.LoadJobConfig()
    job_config.source_format = bigquery.SourceFormat.CSV
    job_config.schema = schema
    job_config.skip_leading_rows = n_skip_rows    # skip header

    for i, uri in enumerate(source_uris):
        print("{}...".format(i))
        print("Source URI: {}".format(uri))

        load_job = client.load_table_from_uri(
            uri, dataset_ref.table(table_id), job_config=job_config
        )  # API request
        print("Starting job {}".format(load_job.job_id))

        load_job.result()  # Waits for table load to complete.
        print("Job finished.")

        destination_table = client.get_table(dataset_ref.table(table_id))
        print("Loaded {} rows.".format(destination_table.num_rows))


def refresh():
    client = bigquery.Client()

    dataset_ref = client.dataset(BQ_DATASET_NAME)
    table = bigquery.Table(dataset_ref.table(TABLE_ID), schema=SCHEMA)

    # 一度テーブルを消す
    client.delete_table(table, not_found_ok=True)

    # Cloud StorageのCSVデータからテーブルを作成する
    source_uris = ['/'.join(['gs:/', SOURCE_BUCKET_NAME, b.name]) for b in list_blobs(SOURCE_BUCKET_NAME)]
    insert_values(client, dataset_ref, TABLE_ID, SCHEMA, source_uris, n_skip_rows=1)


def main():
    refresh()


if __name__ == '__main__':
    main()
