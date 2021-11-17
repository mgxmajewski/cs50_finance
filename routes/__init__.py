from flask import Blueprint

routes = Blueprint('routes', __name__)

from .buy import *
from .history import *
from .index import *
from .login import *
from .logout import *
from .quote import *
from .register import *
from .sell import *
from .suggestions import *
