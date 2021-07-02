import time
import datetime
import io
from io import StringIO
import re
import os

import pandas as pd
import boto3


NULL_CRED = {'Access key ID': None, 'Secret access key': None}
CRED_LOAD_ERROR_MESSAGE = """
Failed to load cred file to run athena

Need credential with the following permissions
- AmazonAthenaFullAccess
- AmazonS3FullAccess
"""
DEFAULT_TIMEOUT_IN_SEC = 300
DEFAULT_WAIT_IN_SEC = 1


def load_aws_cred(cred_file_path):
    """
    Need credential with the following permissions
    - AmazonAthenaFullAccess
    - AmazonS3FullAccess
    """
    if not os.path.exists(cred_file_path):
        print(CRED_LOAD_ERROR_MESSAGE)
        return NULL_CRED

    contents = open(cred_file_path, 'r').readlines()
    contents = [c.strip() for c in contents]
    content = dict(zip(re.split(',', contents[0]), re.split(',', contents[1])))

    if 'Access key ID' not in content or 'Secret access key' not in content:
        print(CRED_LOAD_ERROR_MESSAGE)
        return NULL_CRED

    print('Cred below loaded')
    print(content)

    return {
        'Access key ID': content['Access key ID'],
        'Secret access key': content['Secret access key']
    }


class SingleResult:
    timeout_in_sec = DEFAULT_TIMEOUT_IN_SEC
    wait_in_sec = DEFAULT_WAIT_IN_SEC
    response_keys = list()
    query_for_view_creation = None
    last_query = None
    df_result = pd.DataFrame()

    # cred is dict with access_key and access_secret as keys
    def __init__(self, db_region, db_name, bucket, prefix, cred=None, cred_file=None):
        if cred_file is not None:
            cred = load_aws_cred(cred_file)
        self.aws_access_key = cred['Access key ID']
        self.aws_access_secret = cred['Secret access key']

        self.db_name = '{}'.format(db_name)
        self.result_bucket = '{}'.format(bucket)
        self.result_prefix = '{}'.format(prefix)

        self.athena = boto3.client('athena', region_name=db_region,
                                   aws_access_key_id=self.aws_access_key,
                                   aws_secret_access_key=self.aws_access_secret)

    def __del__(self):
        print('deleting SimpleAthena instance...')
        if self.response_keys:
            print('consider to delete files in S3://{b}/{p};'.format(b=self.result_bucket, p=self.result_prefix))
        else:
            print('no result file remains in S3://{b}/{p};'.format(b=self.result_bucket, p=self.result_prefix))
        for k in self.response_keys:
            print(k)

    def set_timeout_in_sec(self, x):
        self.timeout_in_sec = x

    def set_wait_in_sec(self, x):
        self.wait_in_sec = x

    def get_response_keys(self):
        return self.response_keys

    def get_view(self):
        return self.df_result

    def get_table(self):
        return self.df_result

    def get_query(self, timing='last'):
        if timing == 'view_creation':
            return self.query_for_view_creation
        return self.last_query

    def __wait_for_execution_done(self, response):
        # Waiting for Status State to become SUCCEEDED or FAILED
        exec_id = response['QueryExecutionId']

        start_time = datetime.datetime.now()
        time_elapsed = (datetime.datetime.now() - start_time).seconds
        while time_elapsed < self.timeout_in_sec:
            try:
                execution = self.athena.get_query_execution(QueryExecutionId=exec_id)['QueryExecution']
                status_state = execution['Status']['State']
                if status_state in ('SUCCEEDED', 'FAILED'):
                    if status_state == 'FAILED':
                        print(execution)
                    break
                print('{s}: time elapsed {t} sec'.format(s=status_state, t=time_elapsed))
            except Exception as e:
                print(e)
            time.sleep(self.wait_in_sec)
            time_elapsed = (datetime.datetime.now() - start_time).seconds

    def __delete_log(self, response_key):
        s3 = boto3.resource('s3', aws_access_key_id=self.aws_access_key,
                            aws_secret_access_key=self.aws_access_secret)

        start_time = datetime.datetime.now()
        time_elapsed = (datetime.datetime.now() - start_time).seconds
        while time_elapsed < self.timeout_in_sec:
            res = s3.Object(self.result_bucket, response_key).delete()

            if res['ResponseMetadata']['HTTPStatusCode'] == 204:
                break
            else:
                time.sleep(self.wait_in_sec)
                time_elapsed = (datetime.datetime.now() - start_time).seconds

    def __delete_result(self, response_key, and_metadata=False):
        s3 = boto3.resource('s3', aws_access_key_id=self.aws_access_key,
                            aws_secret_access_key=self.aws_access_secret)

        start_time = datetime.datetime.now()
        time_elapsed = (datetime.datetime.now() - start_time).seconds
        while time_elapsed < self.timeout_in_sec:
            res = s3.Object(self.result_bucket, response_key).delete()
            if res['ResponseMetadata']['HTTPStatusCode'] == 204:
                break
            else:
                time.sleep(self.wait_in_sec)
                time_elapsed = (datetime.datetime.now() - start_time).seconds

        if and_metadata:
            start_time = datetime.datetime.now()
            time_elapsed = (datetime.datetime.now() - start_time).seconds
            while time_elapsed < self.timeout_in_sec:
                res = s3.Object(self.result_bucket, response_key + '.metadata').delete()
                if res['ResponseMetadata']['HTTPStatusCode'] == 204:
                    break
                else:
                    time.sleep(self.wait_in_sec)
                    time_elapsed = (datetime.datetime.now() - start_time).seconds

    def create_view(self, query, delete_log=True):
        # query から不要な行（空行とコメントから始まる行）を取り除く
        query = '\n'.join([q.strip() for q in re.split('\n', query) if q != '' and not q.startswith('--')])

        if query.upper().startswith('CREATE OR REPLACE VIEW') or query.upper().startswith('CREATE VIEW'):
            output_bucket_key = 's3://{b}/{p}'.format(b=self.result_bucket, p=self.result_prefix)
            self.query_for_view_creation = query
            self.last_query = query

            response = self.athena.start_query_execution(
                QueryString=query,
                QueryExecutionContext={
                    'Database': self.db_name
                },
                ResultConfiguration={
                    'OutputLocation': output_bucket_key
                }
            )

            self.__wait_for_execution_done(response)

            response_key = '/'.join([self.result_prefix, response['QueryExecutionId']])

            if delete_log:
                self.__delete_log(response_key + '.csv')
                self.__delete_log(response_key + '.txt')
            else:
                self.response_keys.append(response_key + '.csv/txt')

            view_name = re.split(' ', re.split('\n', query)[0])[-2]

            return view_name

        else:
            print('query should start with "CREATE OR REPLACE VIEW" or "CREATE VIEW"')
            print('----------------------------------------')
            print(query)
            print('----------------------------------------')
            return None

    def read_sql(self, query, keep_result=True):
        # query から不要な行（空行とコメントから始まる行）を取り除く
        query = '\n'.join([q.strip() for q in re.split('\n', query) if q != '' and not q.startswith('--')])

        if query.upper().startswith('SELECT'):
            output_bucket_key = 's3://{b}/{p}'.format(b=self.result_bucket, p=self.result_prefix)
            self.last_query = query

            response = self.athena.start_query_execution(
                QueryString=query,
                QueryExecutionContext={
                    'Database': self.db_name
                },
                ResultConfiguration={
                    'OutputLocation': output_bucket_key
                }
            )

            self.__wait_for_execution_done(response)

            response_key = '/'.join([self.result_prefix, response['QueryExecutionId'] + '.csv'])
            client = boto3.client('s3', aws_access_key_id=self.aws_access_key,
                                  aws_secret_access_key=self.aws_access_secret)
            obj = client.get_object(Bucket=self.result_bucket, Key=response_key)

            self.df_result = pd.read_csv(io.BytesIO(obj['Body'].read()), encoding='utf8', dtype=object)

            if keep_result:
                self.response_keys.append(response_key)
                self.response_keys.append(response_key + '.metadata')
            else:
                self.__delete_result(response_key, and_metadata=True)

            return self.df_result
        else:
            print('query should start with "SELECT"')
            print('----------------------------------------')
            print(query)
            print('----------------------------------------')
            return pd.DataFrame

    def read_result_from_s3(self, bucket_key, encoding='utf8'):
        client = boto3.client('s3', aws_access_key_id=self.aws_access_key,
                              aws_secret_access_key=self.aws_access_secret)
        obj = client.get_object(Bucket=self.result_bucket, Key=bucket_key)

        self.df_result = pd.read_csv(io.BytesIO(obj['Body'].read()), encoding=encoding, dtype=object)

        return self.df_result

    def load_query_file(self, f, encoding='utf8'):
        lines = open(f, encoding=encoding).readlines()

        self.last_query = ''.join(lines)

        return self.last_query

    def create_view_from_file(self, f, encoding='utf8', delete_log=True):
        query = self.load_query_file(f, encoding)

        return self.create_view(query, delete_log)

    def read_sql_from_file(self, f, encoding='utf8', keep_result=True):
        query = self.load_query_file(f, encoding)

        return self.read_sql(query, keep_result)

    def download_table_all(self, table, keep_result=True):
        query = 'select * from {}'.format(table)
        self.last_query = query
        return self.read_sql(query, keep_result)

    def download_view_all(self, view, keep_result=True):
        query = 'select * from {}'.format(view)
        self.last_query = query
        return self.read_sql(query, keep_result)

    def save_result(self, dst_bucket, dst_key):
        s3 = boto3.resource('s3', aws_access_key_id=self.aws_access_key,
                            aws_secret_access_key=self.aws_access_secret)

        csv_buffer = StringIO()
        self.df_result.to_csv(csv_buffer)

        start_time = datetime.datetime.now()
        time_elapsed = (datetime.datetime.now() - start_time).seconds
        res = None
        while time_elapsed < self.timeout_in_sec:
            res = s3.Object(dst_bucket, dst_key).put(Body=csv_buffer.getvalue())

            if res['ResponseMetadata']['HTTPStatusCode'] == 200:
                break
            else:
                time.sleep(self.wait_in_sec)
                time_elapsed = (datetime.datetime.now() - start_time).seconds

        self.response_keys.append('/'.join([dst_bucket, dst_key]))
        return res


def test():
    pass


if __name__ == '__main__':
    test()
