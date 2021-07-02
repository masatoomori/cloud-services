# -*- coding: utf-8 -*-
import email
import boto3
import urllib
import re
import function_to_receive  # メールを処理する関数を定義した任意のスクリプト

RECEIVER = 'receiver email address'


def get_email_address(msg_object, pos):
    """
    メールアドレスのみを抽出する。メールアドレスは
    1. '@'の含まれている
    2. '@'で始まる、または、終わることはない
    文字列とする。
    To, CC, Fromのいずれかに入っている値なので、有効であると仮定し、あまり厳密に確認はしない
    """
    accounts = msg_object.get_all(pos)

    # 空白で分割した最後にメールアドレスがあると仮定
    emails = list()
    if accounts is not None:
        for account in accounts:
            parsed_accounts = [a for a in re.split('[,\t\r\n ]', account)
                               if '@' in a and not a.startswith('@') and not a.endswith('@')]
            for parsed_account in parsed_accounts:
                emails.append(re.sub(r'[<>"]', '', parsed_account).lower())

    return list(set(emails))


def lambda_handler(event, context):
    s3 = boto3.client('s3')

    # S3上のメールファイル取得
    bucket_name = event['Records'][0]['s3']['bucket']['name']
    file_name = urllib.parse.unquote_plus(event['Records'][0]['s3']['object']['key'], encoding='utf-8')

    # メールファイル取得
    try:
        response = s3.get_object(
            Bucket=bucket_name,
            Key=file_name
        )
    except Exception as e:
        raise e

    body = response['Body'].read()

    # stringだったメッセージをオブジェクトに変換する
    rcv_msg_object = email.message_from_bytes(body)

    # 送受信者メールアドレスを取得する
    receiver_tos = get_email_address(rcv_msg_object, 'To')
    receiver_ccs = get_email_address(rcv_msg_object, 'CC')
    senders = get_email_address(rcv_msg_object, 'From')

    print('TO:', receiver_tos)
    print('CC:', receiver_ccs)
    print('FROM', senders)

    if RECEIVER in receiver_tos:
        print('pass email to {}'.format(RECEIVER))
        function_to_receive.main(receiver_tos, receiver_ccs, senders, body)


def test():
    event = {
        'Records': [{
            's3': {
                'bucket': {
                    'name': '<S3 to receive email>'
                },
                'object': {
                    'key': '<email file in S3>'
                }
            }
        }]
    }
    context = {}
    lambda_handler(event, context)


if __name__ == '__main__':
    test()
