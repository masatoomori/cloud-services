#! /bin/sh

# make BigQuery External Table from csv file(s) in Cloud Storage (must be located in us-central1 as of 6 Apr. 2020)
# If preder Parquet, change CSV to PARQUET below
bq mkdef --autodetect --source_format=CSV "gs://<bucket name>/<file name, * can be used>" > path/to/table_info.json
bq mk --external_table_definition=path/to/table_info.json <BigQuery Dataset Name>.<BigQuery Table ID>
