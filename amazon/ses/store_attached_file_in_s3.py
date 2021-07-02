import email
import io

import boto3
import pandas as pd

BUCKET = '<S3 bucket to store>'
KEY = '<S3 key to store>'


def strip(x):
    x = str(x).replace('\n', '').replace('\r', '').replace('\t', ' ')

    return x


def write_df_to_s3_with_boto3(df, bucket, key, sep=','):
    client = boto3.client('s3')
    bytes_to_write = df.to_csv(None, sep=sep, index=False).encode()
    response = client.put_object(Bucket=bucket, Key=key, Body=bytes_to_write)

    return response


def load_data(part, xls_sheet_name, n_skip_row):
    attach_data = part.get_payload(decode=True)

    df = pd.read_excel(io.BytesIO(attach_data), encoding='cp932', dtype=object,
                       sheet_name=xls_sheet_name, skiprows=n_skip_row)

    return df


def save_data(df, bucket, key):
    write_df_to_s3_with_boto3(df, bucket=bucket, key=key, sep='\t')


def excel_to_csv(receiver_tos, receiver_ccs, senders, body, xls_sheet_name, n_skip_row):
    rcv_msg_object = email.message_from_bytes(body)

    for part in rcv_msg_object.walk():
        # ContentTypeがmultipartの場合は実際のコンテンツはさらに中のpartにあるので読み飛ばす
        if part.get_content_maintype() == 'multipart':
            continue
        # ファイル名の取得
        filename = part.get_filename()
        if filename is None:
            continue

        # 添付ファイルがあればそれを取り出してDataFrameを作成する
        df = load_data(part, xls_sheet_name, n_skip_row)

        # 特殊文字を避ける
        for c in ['SUBJECT', 'Body']:
            df[c] = df[c].fillna('').apply(lambda x: strip(x))

        save_data(df, BUCKET, KEY)
