
## JSON ファイルのロード

```python
import json
import boto3

BUCKET = '<bucket name>'
FILE_KEY = '<prefix>/<file name>.json'
OBJ = boto3.resource('s3').Object(BUCKET, FILE_KEY)
CONF = json.loads(OBJ.get()['Body'].read().decode('utf8'))
```

## csv ファイルの分割ダウンロード

```python
def split_lines(line_no, line):
    line = line.decode(FILE_ENCODING)

    # クオートのパターンは下記2つが存在する
    # 1. すべての値がクオートでくくられている場合
    # 2. カンマを含むデータのみがクオートでくくられている場合
    # データの最初の項目はカンマは存在と仮定する。
    # （カンマの数とクオートの数を比べればどちらのパターンかを推測可能かもしれない）
    # この項目がクオートでくくられているかどうかで上記パターンを判断する
    # if くくられている then all_quote = True, else all_quote = False
    line_split = re.split(',', line)

    all_quote = True if line_split[0].startswith('"') and line_split[0].endswith('"') else False

    items = list()
    # クオートの中のカンマをつなぎ直す
    if all_quote:
        for item in line_split:
            if item.startswith('"'):
                if item.endswith('"'):
                    # 間にカンマがない場合
                    item = item.strip('"')
                    items.append(item)
                else:
                    # 間にカンマがあって最初の単語の場合
                    item = item.strip('"')
                    items.append(item)
            else:
                if item.endswith('"'):
                    # 間にカンマがあって最後の単語の場合
                    item = item.strip('"')
                    item = ",".join([items[-1], item])
                    items[-1] = item
                else:
                    # 間にカンマがあって中間の単語の場合
                    item = ",".join([items[-1], item])
                    items[-1] = item

    else:
        first_pos = True
        for item in line_split:
            if item.startswith('"'):
                # クオートで始まった場合、必ず値の最初のパーツであり、カンマが間に含まれる
                # 次の単語はfirst_pos = Falseとなる
                item = item.strip('"')
                items.append(item)
                first_pos = False
            else:
                # クオートで始まらなかった場合、下記の可能性が考えられる
                # 1. カンマのない値
                # 2. カンマのある値の最初のパーツ以外
                if first_pos:
                    items.append(item)
                    first_pos = True
                else:
                    # 最初のパーツでない場合にこのパーツが
                    # 1. クオートで終われば次の単語は最初のパーツ
                    # 2. そうでなければ最初のパーツ以外となる
                    if item.endswith('"'):
                        item = item.strip('"')
                        item = ",".join([items[-1], item])
                        items[-1] = item
                        first_pos = True
                    else:
                        item = ",".join([items[-1], item])
                        items[-1] = item
                        first_pos = False

    return items


obj = client.get_object(Bucket=SOURCE_BUCKET, Key=target_file)

for i, line in enumerate(obj['Body'].iter_lines()):
    if i > 0:                           # 提供日によって異なるカラム名は利用しない
        items = split_lines(i, line)
        lines.append('\t'.join(items))

        if len(lines) > MAX_LINE_COUNT:
            bytes_to_write = '\n'.join(lines).encode('utf8')

            monthly_key = '/'.join([DESTINATION_BUCKET_PREFIX,
                                    PARTITION.format(y=file_date.year, m=file_date.month),
                                    '{p}{d}_{i:04d}.csv'.format(p=FILE_PREFIX, d=file_date.isoformat(),
                                                                i=out_file_index)])
            client.put_object(Bucket=DESTINATION_BUCKET, Key=monthly_key, Body=bytes_to_write)
            print('{n} records uploaded onto {f} in {b}'.format(n=len(lines) - 1, f=monthly_key, b=DESTINATION_BUCKET))

            # ファイルをアップロードしたらリセットする
            lines = [header]
            out_file_index += 1
    if i == 0:
        header = re.split(',', line)
```
