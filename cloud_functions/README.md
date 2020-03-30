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


## メンテナンスする
### Cloud Scheduler Job の削除
不要な Job を削除する。
```shell script
gcloud scheduler jobs delete <削除したいジョブ名>
```