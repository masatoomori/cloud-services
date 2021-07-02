# QuickSight

## Athenaへの接続
### 接続できない場合
下記メッセージが出てAthena経由でS3に接続できない場合、QuickSightの管理画面でアクセスの許可をする必要がある
```bash
[Simba][AthenaJDBC](100071) An error has been thrown from the AWS Athena client.
Access Denied (Service: Amazon S3; Status Code: 403; Error Code: AccessDenied ...
```

詳細はAWSサイト[Amazon Athena に接続できない](https://docs.aws.amazon.com/ja_jp/quicksight/latest/user/troubleshoot-connect-athena.html)を参照
