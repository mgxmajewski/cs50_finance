from flask import render_template, request, redirect, session
from db_connection import db
from helpers import apology, login_required, lookup
from . import routes


@routes.route("/sell", methods=["GET", "POST"])
@login_required
def sell():
    """Sell shares of stock"""

    user_id = session['user_id']
    user_shares = db.execute(
        "SELECT transactions.stock_id, stocks.symbol, stocks.company_name, "
        "sum(transactions.shares) "
        "FROM transactions "
        "JOIN stocks "
        "ON stocks.id = transactions.stock_id "
        "WHERE user_id=:user_id "
        "GROUP BY stock_id",
        user_id=user_id)

    user_stocks = []

    for stocks in user_shares:
        if stocks['sum(transactions.shares)'] > 0:
            user_stocks.append(stocks['symbol'])

    if request.method == "POST":

        stock_to_sell = request.form.get("symbol")
        shares_to_sell = request.form.get("shares")

        # Validate submitted stock to sell
        if not stock_to_sell:
            return apology("You must select stock name", 400)
        elif stock_to_sell is None:
            return apology("Sorry, no such a stock", 400)

        # Validate submitted shares
        if not shares_to_sell.isdigit():
            return apology("You must provide positive integer", 400)
        else:
            shares_to_sell = int(shares_to_sell)

        # Validate if user has enough shares available to sell
        shares_available = db.execute("SELECT sum(transactions.shares) "
                                      "FROM transactions "
                                      "JOIN stocks "
                                      "ON stocks.id = transactions.stock_id "
                                      "WHERE user_id=:user_id "
                                      "AND symbol=:symbol ",
                                      user_id=user_id,
                                      symbol=stock_to_sell)[0]['sum(transactions.shares)']

        if shares_to_sell > shares_available:
            return apology("Exceeded your amount of shares to sell", 400)

        # Shares
        quoted_to_sell = lookup(stock_to_sell)
        iex_symbol = quoted_to_sell['symbol']
        iex_name = quoted_to_sell['name']
        iex_price = quoted_to_sell['price']
        shares_update = -shares_to_sell

        # Balance (cash)
        balance = db.execute("SELECT cash "
                             "FROM users "
                             "WHERE id = :user_id",
                             user_id=user_id)[0]['cash']

        cash_from_sell = shares_to_sell * iex_price
        balance_update = balance + cash_from_sell

        # Update db if transaction is valid
        if shares_to_sell <= shares_available:
            stock_db_id = db.execute("SELECT id "
                                     "FROM stocks "
                                     "WHERE symbol = ?",
                                     iex_symbol)[0]['id']

            db.execute("INSERT INTO transactions (stock_id, user_id, shares, price) "
                       "VALUES (?, ?, ?, ?)",
                       stock_db_id, user_id, shares_update, iex_price)

            db.execute("UPDATE users "
                       "SET cash= ? "
                       "WHERE id= ? ",
                       balance_update, user_id)

        return redirect("/")

    else:
        return render_template("sell.html", user_stocks=user_stocks)
