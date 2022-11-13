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

## 参考

https://rukurx.hatenablog.jp/entry/2020/07/28/112009
