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
START RequestId: xxxxxxxx-xxxx-xxxx-91f8-24d62b663157 Version: $LATEST
[INFO]	2022-mm-ddThh:mm:ss.sssZ	xxxxxxxx-xxxx-xxxx-91f8-24d62b663157	{"key1": "value1", "key2": "value2", "key3": "value3"}
payload to subfunction: {'key1': 'value1', 'key2': 'value2', 'key3': 'value3'}
END RequestId: xxxxxxxx-xxxx-xxxx-91f8-24d62b663157
REPORT RequestId: xxxxxxxx-xxxx-xxxx-91f8-24d62b663157	Duration: 289.13 ms	Billed Duration: 290 ms	Memory Size: 128 MB	Max Memory Used: 66 MB

Request ID
xxxxxxxx-xxxx-xxxx-91f8-24d62b663157
```

## 参考

https://rukurx.hatenablog.jp/entry/2020/07/28/112009
