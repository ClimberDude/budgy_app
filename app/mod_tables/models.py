from app.mod_tables.serverside.serverside_table import ServerSideTable
from app.mod_tables.serverside import table_schemas
 
class TableBuilder(object):
    #####################################################################################
    # Table constructors for transaction data
    #####################################################################################

    def collect_data_serverside_trans_view(self, request, user):
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

        columns = table_schemas.SERVERSIDE_TABLE_COLUMNS_TRANS_VIEW
        return ServerSideTable(request, data, columns).output_result()

    def collect_data_serverside_trans_select(self, request, user):
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

        columns = table_schemas.SERVERSIDE_TABLE_COLUMNS_TRANS_SELECT
        return ServerSideTable(request, data, columns).output_result()

    #####################################################################################
    # Table constructors for budget data
    #####################################################################################

    def collect_data_serverside_budget_view(self, request, user):
        budget_list = user.budget_categories.all()
        history_list = user.budget_histories.filter_by(status = 'C')
        data = []
        for budget in budget_list:
            history = history_list.filter_by(id_budget_category = budget.id).first()
            data.append({
                "category_title": budget.category_title,
                "spending_category": budget.spending_category,
                "annual_budget": history.annual_budget,
                "current_balance": budget.current_balance
                })  

        columns = table_schemas.SERVERSIDE_TABLE_COLUMNS_BUDGET_VIEW
        return ServerSideTable(request, data, columns).output_result()

    def collect_data_serverside_budget_select(self, request, user):
        budget_list = user.budget_categories.all()
        history_list = user.budget_histories.filter_by(status = 'C')
        data = []
        for budget in budget_list:
            history = history_list.filter_by(id_budget_category = budget.id).first()
            data.append({
                "id": budget.id,
                "category_title": budget.category_title,
                "spending_category": budget.spending_category,
                "annual_budget": history.annual_budget,
                "current_balance": budget.current_balance
                })  

        columns = table_schemas.SERVERSIDE_TABLE_COLUMNS_BUDGET_SELECT
        return ServerSideTable(request, data, columns).output_result()

