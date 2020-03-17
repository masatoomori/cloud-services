from google.cloud import bigquery       # pip install google-cloud-bigquery
import os

# GCPのリソースにアクセスするためのCredentialを設定
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = '<service account defined in GCP>.json'

BQ_DATASET_NAME = '<dataset name>'
TABLE_ID = '<table name>'


def download_by_date_range(date_col, date_iso_from, date_iso_to):
    """
    日付を条件にデータをダウンロードしてDataFrameに格納する
    :param date_col: 条件となる日付フォーマットのカラム
    :param date_iso_from: 絞り込み日付下限
    :param date_iso_to: 絞り込み日付上限
    :return: 日付で絞り込まれたデータ
    """

    client = bigquery.Client()
    query = """SELECT
            *
        FROM
            {ds}.{t}
        WHERE
            {c} BETWEEN "{fd}" AND "{td}"     -- 日付範囲指定
    """.format(ds=BQ_DATASET_NAME, t=TABLE_ID, c=date_col, fd=date_iso_from, td=date_iso_to)

    df = client.query(query).result().to_dataframe()

    return df


def main():
    df = download_by_date_range('<date column>', '<YYYY-MM-DD>', '<YYYY-MM-DD>')
    print(df.info())


if __name__ == '__main__':
    main()
