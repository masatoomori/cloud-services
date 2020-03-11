# Pythonからファイルをやり取りする方法

## 準備
1. APIとサービスのダッシュボード画面で、Google Cloud Storage JSON APIが無効でないことを確認する
1. APIとサービスの認証情報画面で、サービスアカウントを作成する
    1. ストレージ→ストレージ管理者の役割を与える
    1. JSONタイプのキーを作成する
1. ダウンロードしたJSONファイルを任意の場所に保管する

## 利用
サービスアカウントのキーファイルを環境変数 GOOGLE_APPLICATION_CREDENTIALS に設定する
```python
import os
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "<ダウンロードしたJSONファイル>"
```
