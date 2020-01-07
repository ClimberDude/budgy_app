from app.mod_tables.serverside.serverside_table import ServerSideTable
from app.mod_tables.serverside import table_schemas
from datetime import datetime
from decimal import Decimal
 
class TableBuilder(object):

    def collect_data_clientside(self):
        return {'data': DATA_SAMPLE}

    def collect_data_serverside_view(self, request, user):
        transactions_list = user.transactions.all()
        budget_list = user.budget_categories
        data = []
        for transaction in transactions_list:
            category = budget_list.filter_by(id = transaction.id_budget_category).first()
            data.append({
                "date": str(transaction.date),
                "amount": transaction.amount,
                "ttype": transaction.ttype,
                "category": category.category_title,
                "vendor": transaction.vendor,
                "note": transaction.note
                })  

        columns = table_schemas.SERVERSIDE_TABLE_COLUMNS_VIEW
        return ServerSideTable(request, data, columns).output_result()

    def collect_data_serverside_select(self, request, user):
        transactions_list = user.transactions.all()
        budget_list = user.budget_categories
        data = []
        for transaction in transactions_list:
            category = budget_list.filter_by(id = transaction.id_budget_category).first()
            data.append({
                "id": transaction.id,
                "date": str(transaction.date),
                "amount": transaction.amount,
                "ttype": transaction.ttype,
                "category": category.category_title,
                "vendor": transaction.vendor,
                "note": transaction.note
                })  

        columns = table_schemas.SERVERSIDE_TABLE_COLUMNS_SELECT
        return ServerSideTable(request, data, columns).output_result()
