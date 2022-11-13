# Lambda から Lambda を呼び出す

非同期で呼び出したい場合

```python
import os
import json
import logging

import boto3

logger = logging.getLogger()
logger.setLevel(logging.INFO)

# 呼び出したい関数名
SUBFUNCTION_NAME = 'LAMBDA_FUNCTION_NAME'

def lambda_handler(event: dict, context):
    # ログ出力
    logging.info(json.dumps(event))

    client = boto3.client('lambda')
    client.invoke(
        FunctionName=SUBFUNCTION_NAME,
        InvocationType='Event',
        LogType='Tail',
        Payload=json.dumps(event)
    )

    return {
        'statusCode': 200,
        'body': json.dumps('OK')
    }
```

## ロールの設定

呼び出す側の実行ロールに下記を足す。
`AWSLambdaRole` をというポリシーをアッタッチしたらできた。

```json
{
    "Effect": "Allow",
    "Action": [
        "lambda:InvokeFunction"
    ],
    "Resource": "*"
}
```

## テスト

### テストイベント

```json
{
  "key1": "value1",
  "key2": "value2",
  "key3": "value3"
}
```

### テスト結果

```text
Test Event Name
test

Response
{
  "statusCode": 200,
  "body": "\"Finished main function\""
}

Function Logs
START RequestId: xxxxxxxx-xxxx-xxxx-8f5a-8dfbbd8613aa Version: $LATEST
[INFO]	2022-mm-ddT07:56:51.922Z	xxxxxxxx-xxxx-xxxx-8f5a-8dfbbd8613aa	{"key1": "value1", "key2": "value2", "key3": "value3"}
payload to subfunction: {'key1': 'value1', 'key2': 'value2', 'key3': 'value3'}
[INFO]	2022-mm-ddT07:56:52.122Z	xxxxxxxx-xxxx-xxxx-8f5a-8dfbbd8613aa	Found credentials in environment variables.
END RequestId: xxxxxxxx-xxxx-xxxx-8f5a-8dfbbd8613aa
REPORT RequestId: xxxxxxxx-xxxx-xxxx-8f5a-8dfbbd8613aa	Duration: 1518.83 ms	Billed Duration: 1519 ms	Memory Size: 128 MB	Max Memory Used: 65 MB	Init Duration: 289.86 ms

Request ID
xxxxxxxx-xxxx-xxxx-8f5a-8dfbbd8613aa
```

## 参考

https://rukurx.hatenablog.jp/entry/2020/07/28/112009
