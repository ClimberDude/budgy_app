from flask import Blueprint

bp = Blueprint('visuals', __name__, template_folder='templates')

from app.visuals import routes