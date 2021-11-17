from flask import render_template, session, request
from db_connection import db
from helpers import login_required, lookup, apology, usd
from . import routes


@routes.route("/quote", methods=["GET", "POST"])
@login_required
def quote():
    """Get stock quote."""

    if request.method == "POST":

        # Get symbol from user submit
        symbol = request.form.get("symbol")

        # Call lookup function
        quoted_stock = lookup(symbol)

        # Ensure symbol was submitted
        if not symbol:
            return apology("must provide valid stock name", 400)
        elif quoted_stock is None:
            return apology("Sorry, no such a stock", 400)

        # Declare variables to render quote of the stock
        iex_symbol = quoted_stock['symbol']
        iex_name = quoted_stock['name']
        iex_price = usd(quoted_stock['price'])
        user_id = session['user_id']

        # Query db for users username
        user_db_import = db.execute("SELECT username "
                                    "FROM users "
                                    "WHERE id = :user_id ",
                                    user_id=user_id)

        user_name = user_db_import[0]['username']

        # Redirect user to login
        return render_template("quoted.html",
                               iex_symbol=iex_symbol,
                               iex_name=iex_name,
                               iex_price=iex_price,
                               user_name=user_name)

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("quote.html")

    return apology("TODO")
