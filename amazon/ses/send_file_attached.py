# 実行ユーザ（IAMなどで指定）にSESへのアクセス権があることを確認すること

import json
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication

import boto3

SES_PROFILE_FILE = 'ses_profile.json'
SES_PROFILE_NAME = "SES_PROFILE_FILEにある誰か"
SES_NAME = json.loads(open(SES_PROFILE_FILE).read())[SES_PROFILE_NAME]["name"]
SES_EMAIL = json.loads(open(SES_PROFILE_FILE).read())[SES_PROFILE_NAME]["email"]
SES_REGION = json.loads(open(SES_PROFILE_FILE).read())[SES_PROFILE_NAME]["region_name"]
SES_ID = json.loads(open(SES_PROFILE_FILE).read())[SES_PROFILE_NAME]["aws_access_key_id"]
SES_KEY = json.loads(open(SES_PROFILE_FILE).read())[SES_PROFILE_NAME]["aws_secret_access_key"]
SENDER_EMAIL = '"{n}" <{e}>'.format(n=SES_NAME, e=SES_EMAIL)

msg_object = MIMEMultipart('alternative')
msg_object['To'] = "メールアドレス"
msg_object['From'] = SENDER_EMAIL
msg_object['Subject'] = "件名"

# メッセージを追加
part = MIMEText("メール本文")
msg_object.attach(part)

# 添付ファイルを追加
part = MIMEApplication(open("ファイルパス", 'rb').read())
part.add_header('Content-Disposition', 'attachment', filename="添付ファイル名")
msg_object.attach(part)

# connect to SES
client = boto3.client('ses',
                      region_name=SES_REGION,
                      aws_access_key_id=SES_ID,
                      aws_secret_access_key=SES_KEY)

# send the message
response = client.send_raw_email(RawMessage={'Data': msg_object.as_string()})
print(response)
