from app.mod_tables.serverside.serverside_table import ServerSideTable
from app.mod_tables.serverside import table_schemas
from datetime import datetime
 
DATA_SAMPLE = [
    {'date': str(datetime.today())[0:10], 'amount': 125.45, 'ttype': 'I', 'category': 'Apples','vendor': 'Wal-Mart', 'note': "",},
    {'date': str(datetime.today())[0:10], 'amount': 200.00, 'ttype': 'E', 'category': 'Apples','vendor': 'Wal-Mart', 'note': "",},
]

class TableBuilder(object):

    def collect_data_clientside(self):
        return {'data': DATA_SAMPLE}

    def collect_data_serverside(self, request, user):
        transactions_list = user.transactions.all()
        data = []
        for transaction in transactions_list:
            data.append({
                "date": str(transaction.date),
                "amount": str(transaction.amount),
                "ttype": str(transaction.ttype),
                "category": "",
                "vendor": str(transaction.vendor),
                "note": str(transaction.note)
                })  

        columns = table_schemas.SERVERSIDE_TABLE_COLUMNS
        return ServerSideTable(request, data, columns).output_result()
