from flask import Blueprint

error = Blueprint('error', __name__)
main = Blueprint('main', __name__)

from . import views, errors
