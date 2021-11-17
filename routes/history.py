from flask import render_template, session
from db_connection import db
from helpers import login_required
from . import routes


@routes.route("/history")
@login_required
def history():
    """Show history of transactions"""

    # Gets user id
    user_id = session['user_id']

    # Query db for all users transactions
    user_history = db.execute("SELECT * "
                              "FROM transactions "
                              "JOIN stocks "
                              "ON stocks.id = transactions.stock_id "
                              "WHERE user_id = :user_id ",
                              user_id=user_id)

    return render_template("history.html", user_history=user_history)