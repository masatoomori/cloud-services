# AWS Lambda

## ディレクトリの構成

AWS Lambda に CLI を使ってスクリプトをデプロイするためのスクリプト。

```bash
$ tree /F
sample_function
├── deploy
│   ├── config.json  : デプロイ先に関する情報を保持するファイル
│   └── update.py    : src以下にあるファイルをアップデートするための実行ファイル
└── src               : スクリプトを保管するディレクトリ
    └── lambda_function.py
```

## パッケージの利用

### Layer

まずは公開されているものがないか確認する。
参考サイト：

- https://aws-sdk-pandas.readthedocs.io/en/stable/layers.html
- https://github.com/mthenw/awesome-layers

なければ自作する。
Lambda が動く環境と同じアーキテクチャでインストールすること。
EC2 が無難。

```bash
mkdir python
pip install -t ./python [package name]
zip -r python.zip python
```

### 関数内に設置

```bash
# パッケージ用ディレクトリを作成し、そこにインストール
mkdir packages
pip install -t ./packages [package name]
```

```python
# PythonでPathを追加
import sys
sys.path.append('./packages')
```

## Terraform

Terraform で Lambda 関数のリソースを定義する場合、S3 上に Lambda 関数の zip ファイルが必要。
[blank-lambda-for-terraform](https://github.com/masatoomori/blank-lambda-for-terraform) などで作成する
