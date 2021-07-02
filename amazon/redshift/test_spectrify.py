from spectrify.create import SpectrumTableCreator
from spectrify.utils.schema import SqlAlchemySchemaReader


def main():
    sa_table = SqlAlchemySchemaReader(engine).get_table_schema('my_table')
    SpectrumTableCreator(sa_engine, dest_schema, dest_table_name, sa_table, s3_config).create()


if __name__ == '__main__':
    main()
