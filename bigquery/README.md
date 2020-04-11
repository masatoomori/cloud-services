# Pythonからファイルをやり取りする方法

## 準備
1. API とサービスのダッシュボード画面で、BigQuery API が無効でないことを確認する
1. API とサービスの認証情報画面で、サービスアカウントを作成する
    1. BigQuery → BigQuery 管理者の役割を与える
    1. ストレージ→ストレージ管理者の役割を与える（Cloud Storage にある External Table 用）
    1. JSON タイプのキーを作成する
1. ダウンロードした JSON ファイルを任意の場所に保管する

## パッケージ
必要なパッケージをインストールする
```bash
$ pip install google-cloud-bigquery
```

## 利用
サービスアカウントのキーファイルを環境変数 GOOGLE_APPLICATION_CREDENTIALS に設定する
```python
import os
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "<ダウンロードしたJSONファイル>"
```

## 注意
BigQuery の外部テーブルとして利用する場合、2020年4月6日現在、us-central1 のものしか参照できない


# Query Sample

## 日付
```
SELECT 

```