import os

from flask import Flask, flash, redirect, render_template, request, session, jsonify
from flask_session import Session
from tempfile import mkdtemp
from werkzeug.exceptions import default_exceptions, HTTPException, InternalServerError
from werkzeug.security import check_password_hash, generate_password_hash
from db_connection import db
from routes import routes

from helpers import apology, login_required, lookup, usd


# Configure application
app = Flask(__name__)

# Ensure templates are auto-reloaded
app.config["TEMPLATES_AUTO_RELOAD"] = True


# Ensure responses aren't cached
@app.after_request
def after_request(response):
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response


# Custom filter
app.jinja_env.filters["usd"] = usd

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_FILE_DIR"] = mkdtemp()
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Make sure API key is set
if not os.environ.get("API_KEY"):
    raise RuntimeError("API_KEY not set")

app.register_blueprint(routes, url_prefix='/')


@app.route("/history")
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


@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in"""

    # Forget any user_id
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # Ensure username was submitted
        if not request.form.get("username"):
            return apology("must provide username", 403)

        # Ensure password was submitted
        elif not request.form.get("password"):
            return apology("must provide password", 403)

        # Query database for username
        rows = db.execute("SELECT * "
                          "FROM users "
                          "WHERE username = :username",
                          username=request.form.get("username"))

        # Ensure username exists and password is correct
        if len(rows) != 1 or not check_password_hash(rows[0]["hash"], request.form.get("password")):
            return apology("invalid username and/or password", 403)

        # Remember which user has logged in
        session["user_id"] = rows[0]["id"]

        # Redirect user to home page
        flash("you are successfully logged in")
        return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("login.html")


@app.route("/logout")
def logout():
    """Log user out"""

    # Forget any user_id
    session.clear()

    # Redirect user to login form
    return redirect("/")


@app.route("/quote", methods=["GET", "POST"])
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


@app.route("/register", methods=["GET", "POST"])
def register():
    """Register user"""

    if request.method == "POST":

        # Declare variables for submitted username and password
        username = request.form.get("username")
        password = request.form.get("password")
        confirmation = request.form.get("confirmation")
        passwd_hash = generate_password_hash(confirmation, method='pbkdf2:sha256', salt_length=8)

        # Ensure user was no registered before
        user_db_import = db.execute("SELECT username "
                                    "FROM users")
        user_names = []

        for users in user_db_import:
            user_names.append(users['username'])

        if username in user_names:
            return apology("must provide unique username", 400)

        # Ensure username was submitted
        if not username:
            return apology("must provide username", 400)

        # Ensure password was submitted
        elif not password:
            return apology("must provide password", 400)

        # Ensure password confirmation are matching
        elif password != confirmation:
            return apology("confirmation must match password", 400)

        # Insert username and hash to database
        db.execute("INSERT INTO users(username, hash) "
                   "VALUES (?, ?)",
                   username,
                   passwd_hash)

        # Redirect user to login
        return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("register.html")


@app.route("/sell", methods=["GET", "POST"])
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


@app.route("/suggestions", methods=["GET"])
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


def errorhandler(e):
    """Handle error"""
    if not isinstance(e, HTTPException):
        e = InternalServerError()
    return apology(e.name, e.code)


# Listen for errors
for code in default_exceptions:
    app.errorhandler(code)(errorhandler)
