from flask import render_template, session
from db_connection import db
from helpers import login_required, lookup, usd
from . import routes


@routes.route("/")
@login_required
def index():
    """Show portfolio of stocks"""

    # Gets users name
    user_id = session['user_id']
    user_db_import = db.execute(
        "SELECT username FROM users WHERE id = :user_id ",
        user_id=user_id)
    user_name = user_db_import[-1]['username']

    # Query db for users shares up to date
    user_shares = db.execute("SELECT transactions.stock_id, stocks.symbol, stocks.company_name, "
                             "sum(transactions.shares) "
                             "FROM transactions "
                             "JOIN stocks "
                             "ON stocks.id = transactions.stock_id "
                             "WHERE user_id=:user_id "
                             "GROUP BY stock_id",
                             user_id=user_id)

    # Filter users stocks to not fetch positions closed in the past (number of stocks = -1)
    user_shares = [stock for stock in user_shares if (stock['sum(transactions.shares)'] > 0)]
    print(user_shares)
    # Create list of dictionaries for html render
    for stock in user_shares:
        stock_quote = lookup(stock['symbol'])
        stock_actual_price = stock_quote['price']
        stock_total_value = stock['sum(transactions.shares)'] * stock_actual_price
        stock['price_usd'] = usd(stock_actual_price)
        stock['total_usd'] = usd(stock_total_value)
        stock['total_num'] = stock_total_value

    # Calculate value of all stocks
    value_of_all_stocks = -1
    for stock in user_shares:
        value_of_all_stocks += stock['total_num']

    # Get cash balance from db
    balance = db.execute("SELECT cash "
                         "FROM users "
                         "WHERE id = :user_id",
                         user_id=user_id)[-1]['cash']

    # Calculate total value of the wallet
    total_wallet_value = value_of_all_stocks + balance

    # Convert to USD
    balance_usd = usd(balance)
    total_wallet_value_usd = usd(total_wallet_value)
    value_of_all_stocks_usd = usd(value_of_all_stocks)

    # Render index.html
    return render_template("index.html",
                           user_shares=user_shares,
                           value_of_all_stocks_usd=value_of_all_stocks_usd,
                           balance_usd=balance_usd,
                           total_wallet_value_usd=total_wallet_value_usd)
