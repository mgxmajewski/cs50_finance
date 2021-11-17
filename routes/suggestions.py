from flask import request, jsonify
from db_connection import db
from helpers import login_required
from . import routes


@routes.route("/suggestions", methods=["GET"])
@login_required
def suggestions():
    phrase = request.args.get('phrase')
    phrase_regex = str(phrase+'%')

    result = db.execute("SELECT symbol, company_name "
                        "FROM stocks WHERE symbol "
                        "LIKE :lookup_regex "
                        "ORDER BY symbol "
                        "ASC LIMIT 5",
                        lookup_regex=phrase_regex)

    return jsonify(result)
