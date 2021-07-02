# coding=utf-8
"""
MySQLdb required (pip install mysqlclient)
"""
from sqlalchemy import create_engine
import pandas as pd
import argparse
import json

CONF_FILE = 'conf.json'
# conf.json
# {
#   "MONEY" : {
#     "host": "xxx.xxx.xxx.xxx",
#     "database": "<database name>",
#     "user": "<user name>",
#     "password": "<password>",
#     "port": 3306
#   }
# }

CONNECTION = 'MONEY'
confs = json.load(open(CONF_FILE, 'r'))
DB_SETTINGS = {
    'host': confs[CONNECTION]["host"],
    'database': confs[CONNECTION]["database"],
    'user': confs[CONNECTION]["user"],
    'password': confs[CONNECTION]["password"],
    'port': confs[CONNECTION]["port"],
}
DB_URI = 'mysql://{user}:{password}@{host}/{database}?charset=utf8'.format(**DB_SETTINGS)
INPUT_FILE = '<csv file path>'


def upload(table_name, input_file):
    engine = create_engine(DB_URI)

    df = pd.read_csv(input_file, dtype=object)
    df.to_sql(table_name, engine, if_exists='replace', index=False)

    print(pd.read_sql('''SELECT * FROM {}'''.format(table_name), engine).tail())


def main():
    parser = argparse.ArgumentParser(
        prog='mysql_in_gce.py',
        usage='this script is to upload csv file to MySQL server in GCE',
        add_help=True
    )
    parser.add_argument('-t', '--table_name',
                        required=True)
    parser.add_argument('-i', '--input_file',
                        required=True)
    args = parser.parse_args()
    upload(args.table_name, args.input_file)


if __name__ == '__main__':
    main()
