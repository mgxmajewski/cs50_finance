from flask import request, jsonify
from db_connection import db
from helpers import login_required
from . import routes


@routes.route("/suggestions", methods=["GET"])
@login_required
def suggestions():
    phrase = request.args.get('phrase')
    phrase_regex = str(phrase)

    symbol_result = db.execute("SELECT symbol, company_name "
                               "FROM stocks WHERE symbol "
                               "LIKE ? "
                               "ORDER BY symbol "
                               "ASC LIMIT 3",
                               '%' + phrase_regex + '%')

    company_name_result = db.execute("SELECT symbol, company_name "
                                     "FROM stocks WHERE company_name "
                                     "LIKE ? "
                                     "ORDER BY company_name "
                                     "ASC LIMIT 3",
                                     '%' + phrase_regex + '%')

    merged_result = []
    symbol_result.extend(company_name_result)
    for suggestion_from_db in symbol_result:
        if suggestion_from_db not in merged_result:
            merged_result.append(suggestion_from_db)

    return jsonify(merged_result)
