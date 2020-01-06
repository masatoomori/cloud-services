from google.cloud import bigquery       # pip install google-cloud-bigquery
import os

os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = '<service account defined in GCP>.json'
BQ_DATASET_NAME = '<dataset name>'
TABLE_ID = '<table name>'


def main():
    client = bigquery.Client()
    query = """SELECT
            *
        FROM
            {ds}.{t}
        WHERE
            <date column> BETWEEN "<date in ISO format>" AND "<date in ISO format>"     -- 日付範囲指定
    """.format(ds=BQ_DATASET_NAME, t=TABLE_ID)

    df = client.query(query).result().to_dataframe()

    print(df)


if __name__ == '__main__':
    main()
