from flask import Blueprint, jsonify, request
from app import table_builder
from flask_security import current_user, login_required


tables = Blueprint('tables', __name__, url_prefix='/tables')


@tables.route("/clientside_table", methods=['GET'])
def clientside_table_content():
    data = table_builder.collect_data_clientside()
    return jsonify(data)


@tables.route("/serverside_table", methods=['GET'])
@login_required
def serverside_table_content():
    data = table_builder.collect_data_serverside(request, current_user)
    return jsonify(data)
