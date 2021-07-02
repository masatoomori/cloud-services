from Athena import SingleResult


DATABASE_REGION = '<aws region>'
DATABASE_NAME = '<database name in glue>'
ATHENA_BUCKET = '<bucket to store athena result / log>'
ATHENA_BUCKET_PREFIX = 'prefix to store athena result / log'

QUERY_FILE = 'test.sql'

QUERY = """SELECT
*
FROM {}
""".format('<test table>')


def main():
    atn = SingleResult(DATABASE_REGION, DATABASE_NAME, ATHENA_BUCKET, ATHENA_BUCKET_PREFIX)

    df_1 = atn.read_sql_from_file(QUERY_FILE, keep_result=False)
    df_2 = atn.read_sql(QUERY, keep_result=False)


if __name__ == '__main__':
    main()
