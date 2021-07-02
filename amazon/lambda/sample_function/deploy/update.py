"""
├── cred
│   ├── "<credential file 1 to upload to AWS Lambda>"
│   └── "<credential file 2 to upload to AWS Lambda>"
├── deploy
│   ├── config.json
│   └── update.py (this file)
└── src
    └── lambda_function.py
"""

import os
import shutil
import json

AWS_CMD_PATH = '/path/to/aws'

TARGET_SOURCE_DIR = os.path.join(os.pardir, 'src')
DEPLOY_DIR = os.curdir
BUILD_FILE_PREFIX = 'lambda'
BUILD_FILE = os.path.join(DEPLOY_DIR, '{}.zip'.format(BUILD_FILE_PREFIX))
CONFIG_FILE = 'config.json'

with open(CONFIG_FILE, 'r') as F:
    CONFIG = json.load(F)

CRED_PATH = os.path.join(os.pardir, 'cred')


def main():
    if os.path.exists(BUILD_FILE):
        os.remove(BUILD_FILE)

    # credファイルをスクリプトと同じ場所にコピーする
    for cred_file in CONFIG['cred_files']:
        source_file = os.path.join(CRED_PATH, cred_file)
        target_file = os.path.join(TARGET_SOURCE_DIR, cred_file)
        if os.path.exists(target_file):
            print('{f} exists in {d}'.format(f=cred_file, d=TARGET_SOURCE_DIR))
        else:
            shutil.copyfile(source_file, target_file)

    shutil.make_archive(os.path.join(DEPLOY_DIR, BUILD_FILE_PREFIX), 'zip', root_dir=TARGET_SOURCE_DIR)

    aws_lambda_update = "{cmd} lambda update-function-code " \
                        "--region {r} --function-name {f} --zip-file fileb://{z} " \
                        "--profile {p}".format(cmd=AWS_CMD_PATH,
                                               r=CONFIG['region'],
                                               f=CONFIG['function'],
                                               z=BUILD_FILE,
                                               p=CONFIG['profile'])

    # アップロードを実行し、zipファイルを削除する
    os.system(aws_lambda_update)
    os.remove(BUILD_FILE)

    # スクリプトと同じ場所にあるcredファイルを削除する
    for cred_file in CONFIG['cred_files']:
        os.remove(os.path.join(TARGET_SOURCE_DIR, cred_file))


if __name__ == '__main__':
    main()
