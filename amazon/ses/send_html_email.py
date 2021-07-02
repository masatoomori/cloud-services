import boto3
from botocore.exceptions import ClientError

SES_REGION = ''
SES_ID = ''
SES_KEY = ''


def main():
    email_to = '<email address>'
    email_from = '<email address>'
    message = 'html message'
    title = 'email title'

    # connect to SES
    client = boto3.client('ses',
                          region_name=SES_REGION,
                          aws_access_key_id=SES_ID,
                          aws_secret_access_key=SES_KEY)

    # メールを作成して送る
    try:
        response = client.send_email(
            Destination={
                'ToAddresses': [email_to]
            },
            Message={
                'Body': {
                    'Html': {
                        'Charset': 'utf8',
                        'Data': message
                    }
                },
                'Subject': {
                    'Charset': 'utf8',
                    'Data': title
                }
            },
            Source=email_from
        )
    except ClientError as e:
        print(e.response['Error']['Message'])
    else:
        print('Email sent. ID: {}'.format(response['MessageId']))


if __name__ == '__main__':
    main()
