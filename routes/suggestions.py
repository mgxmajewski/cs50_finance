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

    print(type(company_name_result))
    # merged_result = list(set(company_name_result).union(set(symbol_result)))
    merged_result = company_name_result + [suggestion for suggestion
                                           in symbol_result if suggestion not in company_name_result]

    merged_result = company_name_result+symbol_result

    return jsonify(merged_result)
