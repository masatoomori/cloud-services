# AWS Lambda

## ディレクトリの構成

AWS Lambda に CLI を使ってスクリプトをデプロイするためのスクリプト。

```bash
$ tree /F
sample_function
├── cred              : 各種アクセス権などを記録したファイルを保存するディレクトリ
├── deploy
│   ├── config.json  : デプロイ先に関する情報を保持するファイル
│   └── update.py    : src以下にあるファイルをアップデートするための実行ファイル
└── src               : スクリプトを保管するディレクトリ
    └── lambda_function.py
```

## Layer

```bash
mkdir python
pip install -t ./python [package name]
zip -r python.zip python
```
