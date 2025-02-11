import happybase
from config.config_loader import config
def fetch_data_from_hbase(table_name, row_start, row_stop):
    connection = happybase.Connection(**config['hbase_store_harmonized_data'])
    table = connection.table(table_name)
    data = list(table.scan(row_start=row_start, row_stop=row_stop))
    # row = table.row(row_key)
    connection.close()
    return data
