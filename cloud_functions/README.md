Cloud Functions 使い方練習
--

# 環境準備
## プロジェクトの作成
プロジェクト Test Cloud Functions を作成する。

# 設定
## 定期的に実行する
作成した関数が定期的に実行されるよう、下記を設定する。
1. Cloud Functions をローカルで作成
1. Cloud Functions と Cloud Scheduler を繋ぐ Pub/Sub Topic を作成
1. Cloud Functions をデプロイし、トリガーに Pub/Sub Topic を指定
1. Cloud Scheduler Job を定期実行するよう設定し、トピックに Pub/Sub Topic を指定

### Cloud Pub/Sub Topic の作成
```shell script
gcloud pubsub topics create <トピック名>
```
- <トピック名>に test-topic を指定する


### Cloud Functions の作成
main.py に関数を記述し、main.py が存在するディレクトリで下記スクリプトを実行する。
```shell script
$ gcloud functions deploy <クラウド関数名> \
    --runtime=<ランタイム名> \
    --trigger-topic=<トピック名>
```
- <クラウド関数名> に test_func (main.py 内の関数) を指定する
- <ランタイム名> にpython37 を指定する
- <トピック名> に test-topic (上記作成したトピック) を指定する


### Cloud Scheduler Job の作成
Pub/Sub を起動するための Scheduler Job を作成する。
```shell script
gcloud scheduler jobs create pubsub <ジョブ名> \
    --schedule=<cron形式のスケジュール> \
    --topic=<トピック名> \
    --time-zone=<タイムゾーン> \
    --message-body=<送信メッセージ>
```
- <ジョブ名> に test-pubsub-job 
- <cron形式のスケジュール> に "0 9 * * 5" (毎週金曜日朝9時) を指定する
- <トピック名> に test-topic (上記作成したトピック) を指定する
- <タイムゾーン> に "Asia/Tokyo" を指定する
- <送信メッセージ>" に "cron test" を指定する

## Google Cloud Storage にファイルがアップロードされた時に実行する
トリガーは Bucket 単位でしか設定できない（ファイル単位やディレクトリ単位は不可）なので、
Cloud Functions を Bucket トリガー単位で作成し、アップロードされたファイル名を
実行時に取得して、その内容によって続く処理を選択する関数を作成する。

関数実行時に受け取る第一引数は下記：
```python
event = {
    'bucket': '<bucket name>',
    'contentType': 'text/plain',
    'crc32c': 'xxxxxx==',
    'etag': 'xxxxx/xxxxxxxxx=',
    'generation': '<integer>',
    'id': '<bucket name>/<file name>/<generation>',
    'kind': 'storage#object',
    'md5Hash': 'xxxxxxxxxxxxxxxxxxxxxx==',
    'mediaLink': 'https://www.googleapis.com/download/storage/v1/b/<bucket name>/o/<file name>?generation=<generation>&alt=media',
    'metageneration': '1',
    'name': '<file name>',
    'selfLink': 'https://www.googleapis.com/storage/v1/b/<bucket name>/o/<file name>',
    'size': '<integer>',
    'storageClass': 'STANDARD',
    'timeCreated': 'YYYY-MM-DDThh:mm:ss.sssZ',
    'timeStorageClassUpdated': 'YYYY-MM-DDThh:mm:ss.sssZ',
    'updated': 'YYYY-MM-DDThh:mm:ss.sssZ'
}
```

### Cloud Functions の作成
main.py に関数を記述し、main.py が存在するディレクトリで下記スクリプトを実行する。
```shell script
gcloud functions deploy <main.py に存在するデプロイする関数名> \
    --runtime=python37 \
    --trigger-resource=<bucket name for trigger> \
    --trigger-event=google.storage.object.finalize \
    --timeout=540s \
    --memory=2048MB
```


## メンテナンスする
### Cloud Scheduler Job の削除
不要な Job を削除する。
```shell script
gcloud scheduler jobs delete <削除したいジョブ名>
```