# athena handler

## 既存のパッケージを使う場合

```python
from pyathena import connect
from pyathena.pandas.cursor import PandasCursor
import pandas as pd

s3_stating_dir = 's3://bucket/path/to/data'
region_name = 'aws region name'
profile_name = 'aws profile name usually stored in ~/.aws/config'

conn = connect(s3_stating_dir=s3_stating_dir, region_name=region_name, profile_name=profile_name)
cur = conn.cursor(PandasCursor)
df = pd.read_sql_query('select * from table_name', conn)
```

## Class を新たに定義して使う場合

AWS Athena はカタログ化した S3 データなどを簡単に組み合わせて出力できるので大変便利です。
ただし、ブラウザからではなく、スクリプトの中で使おうとするといろいろと面倒な作業があるので、
そのような作業を Class を作成し、まとめました。

AWS Lambda Layer で使う場合、python ディレクトリを zip してアップロードします。

現在は下記の Class があります

- SingleResult: VIEW の作成や、TABLE / VIEW のデータダウンロードを行います。内部に DataFrame として結果を保持します。一度に保持できる結果は 1 つのみです

### SingleResult

インスタンスを作成する際に下記の情報が必要です

- データベースのリージョン
- カタログで設定したデータベース名
- 一次結果ファイルを保存する S3 のバケツ
- 一次結果ファイルを保存する S3 のプレフィックス

```python
from Athena import SingleResult

DATABASE_REGION = '<aws region>'
DEFAULT_DATABASE = '<database name in glue>'
ATHENA_BUCKET = '<bucket to store athena result / log>'
ATHENA_PREFIX = '<prefix to store athena result / log>'
cred_file = '<path to cred_file for S3 access and Athena access>'

atn = SingleResult(DATABASE_REGION, DEFAULT_DATABASE, ATHENA_BUCKET, ATHENA_PREFIX, cred_file)
```

クエリを読み込みます

```python
f = '<path to sql file>'
query = atn.load_query_file(f)
```

テキストのクエリを引数に取り、作成した VIEW の名前を返します

```python
view = atn.create_view(query)
```

テキストのクエリを引数に取り、DataFrame に結果を格納します。一次結果ファイルを残すかどうか選択できます

```python
df = atn.read_sql('select * from test_view', keep_result=False)
```

クエリをファイルから読み込んで DataFrame に結果を格納します。

```python
f = '<path to sql file>'
df = atn.read_sql_from_file(f, keep_result=False)
```

S3 のバケツとキーを指定して、CSV 形式で結果を保存できます

```python
atn.save_result(ATHENA_BUCKET, ATHENA_PREFIX + '/view_result.csv')
```

## クエリ

[Athenaでデータ抽出するときによく使う関数まとめ](https://qiita.com/sh_tomato/items/97c33cea9bed5a23dd9e)も参考に

### 日付

#### `created_iso_date` が本日より １ ヵ月以内

```sql
created_iso_date > CURRENT_DATE - interval '1' month
```

#### `Expiration_Date`が 2018年1月1日以降

```sql
Expiration_Date >= CAST('2018-01-01' AS date)
```

### 文字列

#### 連結

```sql
string1 || string2
```

#### 切出し

```sql
SUBSTR(string, <start pos (1 origin)>, <length>)
```

#### 大文字小文字

```sql
UPPER(string1)
LOWER(string2)
```

### 代入

#### NULL を埋める

2 つ以上の引数を取り、一番最初の NULL でない値を返す

```sql
COALESCE(a, b)
```

### 型変換

```sql
CAST(string AS <data type>)
```

## ポリシー

このクラスを利用するには、実行アカウントに下記ポリシーが必要です

```json
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Sid": "VisualEditor0",
            "Effect": "Allow",
            "Action": "athena:ListWorkGroups",
            "Resource": "*"
        },
        {
            "Sid": "VisualEditor1",
            "Effect": "Allow",
            "Action": [
                "athena:*"
            ],
            "Resource": [
                "arn:aws:athena:<aws region>:<aws account number>:workgroup/primary",
                "arn:aws:s3:::<bucket to store athena result / log>"
            ]
        },
        {
            "Sid": "VisualEditor4",
            "Effect": "Allow",
            "Action": [
                "glue:*"
            ],
            "Resource": [
                "arn:aws:glue:<aws region>:<aws account number>:catalog",
                "arn:aws:<aws region>:<aws account number>:database/<database name in glue>",
                "arn:aws:<aws region>:<aws account number>:table/<database name in glue>/*"
            ]
        },
        {
            "Sid": "VisualEditor2",
            "Effect": "Allow",
            "Action": "s3:GetObject",
            "Resource": "arn:aws:s3:::<bucket name for data source>/<prefix for data source>/*"
        },
        {
            "Sid": "VisualEditor3",
            "Effect": "Allow",
            "Action": [
                "s3:PutObject",
                "s3:GetObject",
                "s3:ListBucketMultipartUploads",
                "s3:AbortMultipartUpload",
                "s3:ListBucket",
                "s3:DeleteObject",
                "s3:GetBucketLocation",
                "s3:ListMultipartUploadParts"
            ],
            "Resource": [
                "arn:aws:s3:::<bucket to store athena result / log>/<prefix to store athena result / log>/*",
                "arn:aws:s3:::<bucket to store athena result / log>"
            ]
        }
    ]
}
```
