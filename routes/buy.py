from flask import render_template, session, request, redirect
from db_connection import db
from helpers import login_required, lookup, apology
from . import routes


@routes.route("/buy", methods=["GET", "POST"])
@login_required
def buy():
    """Buy shares of stock"""

    if request.method == "POST":

        # Declare variables for submitted username and password
        user_id = session['user_id']
        user_name = db.execute("SELECT username "
                               "FROM users "
                               "WHERE id = :user_id ",
                               user_id=user_id)[0]['username']

        balance = db.execute("SELECT cash "
                             "FROM users "
                             "WHERE id = :user_id",
                             user_id=user_id)[0]['cash']

        symbol = request.form.get("symbol")
        shares = request.form.get("shares")

        # Validate symbol
        if not symbol:
            return apology("must provide valid stock name", 400)
        elif symbol is None:
            return apology("Sorry, no such a stock", 400)

        # Validate shares
        if not shares.isdigit():
            return apology("You must provide positive integer", 400)
        else:
            shares = int(shares)

        # Call lookup to get price
        stock_import = lookup(symbol)

        # Validate ticker symbol is valid
        if stock_import is None:
            return apology("Sorry, ticker symbol invalid", 400)

        # Declare variables to render quote of the stock
        iex_symbol = stock_import['symbol']
        iex_name = stock_import['name']
        iex_price = stock_import['price']

        # Calculate values for db update
        stock_purchase_value = iex_price * shares
        balance_after_trans = balance - stock_purchase_value

        # Insert stock into stocks (only if company wasn't bought before)
        db.execute("INSERT OR IGNORE "
                   "INTO stocks(symbol, company_name) "
                   "VALUES (:symbol, :company_name)",
                   symbol=iex_symbol,
                   company_name=iex_name)

        # Validate user cash balance
        if balance >= stock_purchase_value:
            stock_db_id = db.execute("SELECT id "
                                     "FROM stocks "
                                     "WHERE symbol = ?",
                                     iex_symbol)[0]['id']

            # Update db with purchased stock
            db.execute("INSERT INTO transactions (stock_id, user_id, shares, price) "
                       "VALUES (?, ?, ?, ?)",
                       stock_db_id, user_id, shares, iex_price)

            db.execute("UPDATE users "
                       "SET cash= ? "
                       "WHERE id= ? ",
                       balance_after_trans,
                       user_id)
        else:
            return apology("Sorry, you dont have enough cash", 400)

        # Redirect user index.html
        return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("buy.html")
