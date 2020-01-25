from app.mod_tables.serverside.serverside_table import ServerSideTable
from app.mod_tables.serverside import table_schemas
from flask import current_app
 
class TableBuilder(object):
    #####################################################################################
    # Table constructors for transaction data
    #####################################################################################

    def collect_data_serverside_trans_view(self, request, user):
        with current_app.app_context():
            from app import db
            from app.models import User, Budget_Category, Budget_History, Transaction
            #Do not display repeating transaction templates. 
            transactions_list = db.session.query(Transaction).filter(Transaction.id_user == user.id).filter(Transaction.ttype != 'SE' or Transaction.ttype != 'SI').all()
            data = []
            for transaction in transactions_list:
                data.append({
                    "date": str(transaction.date),
                    "amount": transaction.amount,
                    "ttype": transaction.ttype,
                    "category": transaction.budget_category.category_title,
                    "vendor": transaction.vendor,
                    "note": transaction.note
                    })  

            columns = table_schemas.SERVERSIDE_TABLE_COLUMNS_TRANS_VIEW
            return ServerSideTable(request, data, columns).output_result()

    def collect_data_serverside_trans_select(self, request, user):
        with current_app.app_context():
            from app import db
            from app.models import User, Budget_Category, Budget_History, Transaction
            #Do not display repeating transaction templates. 
            transactions_list = db.session.query(Transaction).filter(Transaction.id_user == user.id).filter(Transaction.ttype != 'SE' or Transaction.ttype != 'SI').all()
            data = []

            for transaction in transactions_list:
                data.append({
                    "id": transaction.id,
                    "date": str(transaction.date),
                    "amount": transaction.amount,
                    "ttype": transaction.ttype,
                    "category": transaction.budget_category.category_title,
                    "vendor": transaction.vendor,
                    "note": transaction.note
                    })  

            columns = table_schemas.SERVERSIDE_TABLE_COLUMNS_TRANS_SELECT
            return ServerSideTable(request, data, columns).output_result()

    #####################################################################################
    # Table constructors for budget data
    #####################################################################################

    def collect_data_serverside_budget_view(self, request, user):
        with current_app.app_context():
            from app import db
            from app.models import User, Budget_Category, Budget_History, Transaction
            history_list = db.session.query(Budget_History).filter(Budget_History.id_user == user.id).filter_by(status='C').all()
            data = []
            for history in history_list:
                data.append({
                    "category_title": history.budget_category.category_title,
                    "spending_category": history.budget_category.spending_category,
                    "annual_budget": history.annual_budget,
                    "current_balance": history.budget_category.current_balance
                    })  

        columns = table_schemas.SERVERSIDE_TABLE_COLUMNS_BUDGET_VIEW
        return ServerSideTable(request, data, columns).output_result()

    def collect_data_serverside_budget_select(self, request, user):
        with current_app.app_context():
            from app import db
            from app.models import User, Budget_Category, Budget_History, Transaction
            history_list = db.session.query(Budget_History).filter(Budget_History.id_user == user.id).filter_by(status='C').all()
            data = []
            for history in history_list:
                data.append({
                    "id": history.budget_category.id,
                    "category_title": history.budget_category.category_title,
                    "spending_category": history.budget_category.spending_category,
                    "annual_budget": history.annual_budget,
                    "current_balance": history.budget_category.current_balance
                    })  

        columns = table_schemas.SERVERSIDE_TABLE_COLUMNS_BUDGET_SELECT
        return ServerSideTable(request, data, columns).output_result()

