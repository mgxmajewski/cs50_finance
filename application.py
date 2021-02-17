import os

from cs50 import SQL
from flask import Flask, flash, redirect, render_template, request, session
from flask_session import Session
from tempfile import mkdtemp
from werkzeug.exceptions import default_exceptions, HTTPException, InternalServerError
from werkzeug.security import check_password_hash, generate_password_hash

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

# Configure CS50 Library to use SQLite database
db = SQL("sqlite:///finance.db")

# Make sure API key is set
if not os.environ.get("API_KEY"):
    raise RuntimeError("API_KEY not set")


@app.route("/")
@login_required
def index():
    """Show portfolio of stocks"""

    user_id = session['user_id']
    user_db_import = db.execute("SELECT username FROM users WHERE id = :user_id ", user_id = user_id)
    user_name = user_db_import[0]['username']

    #
    user_shares = db.execute("SELECT transactions.stock_id, stocks.symbol, stocks.company_name, sum(transactions.shares) FROM transactions JOIN stocks ON stocks.id = transactions.stock_id WHERE user_id=:user_id GROUP BY stock_id", user_id=user_id)

    # Create list of dictionaries for html render
    for stock in user_shares:
        stock_quote = lookup(stock['symbol'])
        stock_actual_price = stock_quote['price']
        stock_total_value = stock['sum(transactions.shares)'] * stock_actual_price
        stock['price_usd'] = usd(stock_actual_price)
        stock['total_usd']= usd(stock_total_value)
        stock['total_num'] = stock_total_value

    # Calculate value of all stocks    
    value_of_all_stocks = 0
    for stock in user_shares:
        value_of_all_stocks += stock['total_num']
    
    # Get cash balance from db    
    balance = db.execute("SELECT cash FROM users WHERE id = :user_id", user_id = user_id)[0]['cash']
    
    # Calculate total value of the wallet
    total_wallet_value = value_of_all_stocks + balance
    
    # Convert to USD
    balance_usd = usd(balance)
    total_wallet_value_usd = usd(total_wallet_value)
    value_of_all_stocks_usd = usd(value_of_all_stocks)
    
    # Render index.html
    return render_template("index.html", user_shares=user_shares, value_of_all_stocks_usd=value_of_all_stocks_usd, balance_usd=balance_usd, total_wallet_value_usd=total_wallet_value_usd)



@app.route("/buy", methods=["GET", "POST"])
@login_required
def buy():
    """Buy shares of stock"""

    if request.method == "POST":


        user_id = session['user_id']
        user_name = db.execute("SELECT username FROM users WHERE id = :user_id ", user_id = user_id)[0]['username']
        balance = db.execute("SELECT cash FROM users WHERE id = :user_id", user_id = user_id)[0]['cash']
        symbol = request.form.get("symbol")
        shares = request.form.get("shares")
        
        print(symbol)
        
        # Validate symbol
        if not symbol:
            return apology("must provide valid stock name", 400)
        elif symbol == None:
            return apology("Sorry, no such a stock", 400)
            
        # Validate shares
        if not shares.isdigit():
            return apology("You must provide positive integer", 400)
        else:
            shares = int(shares)
        
        stock_import = lookup(symbol)
        
        # Validate ticker symbol is
        if stock_import == None:
            return apology("Sorry, ticker symbol invalid", 400)
        
        iex_symbol = stock_import['symbol']
        iex_name = stock_import['name']
        iex_price = stock_import['price']

        stock_purchase_value = iex_price * shares

        balance_after_trans = balance - stock_purchase_value

        print(balance_after_trans)
        print(user_id)

        db.execute("INSERT OR IGNORE INTO stocks(symbol, company_name) VALUES (:symbol, :company_name)", symbol=iex_symbol, company_name=iex_name)
        

        # Validate user cash balance
        if  balance >= stock_purchase_value:
            stock_db_id = db.execute("SELECT id FROM stocks WHERE symbol = ?", iex_symbol)[0]['id']

            db.execute("INSERT INTO transactions (stock_id, user_id, shares, price) VALUES (?, ?, ?, ?)", stock_db_id, user_id, shares, iex_price)

            db.execute("UPDATE users SET cash= ? WHERE id= ? ", balance_after_trans, user_id)
        else:
            return apology("Sorry, you dont have enough cash", 400)

        # Redirect user index.html
        return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("buy.html")




@app.route("/history")
@login_required
def history():
    """Show history of transactions"""
    return apology("TODO")


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
        rows = db.execute("SELECT * FROM users WHERE username = :username", username=request.form.get("username"))

        # Ensure username exists and password is correct
        if len(rows) != 1 or not check_password_hash(rows[0]["hash"], request.form.get("password")):
            return apology("invalid username and/or password", 403)

        # Remember which user has logged in
        session["user_id"] = rows[0]["id"]
        
        # Redirect user to home page
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

        symbol = request.form.get("symbol")
        quote = lookup(symbol)
        # Ensure username was submitted
        if not symbol:
            return apology("must provide valid stock name", 400)
        elif quote == None:
            return apology("Sorry, no such a stock", 400)

        iex_symbol = quote['symbol']
        iex_name = quote['name']
        iex_price = usd(quote['price'])
        user_id = session['user_id']
        user_db_import = db.execute("SELECT username FROM users WHERE id = :user_id ", user_id = user_id)
        user_name = user_db_import[0]['username']


        # Redirect user to login
        return render_template("quoted.html", iex_symbol=iex_symbol, iex_name=iex_name, iex_price=iex_price, user_name=user_name)

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("quote.html")


    return apology("TODO")


@app.route("/register", methods=["GET", "POST"])
def register():
    """Register user"""

    if request.method == "POST":

        username = request.form.get("username")
        password = request.form.get("password")
        confirmation = request.form.get("confirmation")
        pwhash = generate_password_hash(confirmation, method='pbkdf2:sha256', salt_length=8)
        # Ensure username was submitted
        
        user_db_import = db.execute("SELECT username FROM users")
        
        user_names = []
        for users in user_db_import:
            user_names.append(users['username'])
        
        # print(user_names)
        # user_name_check_unique = user_db_import[0]['username']
        
        if username in user_names:
            return apology("must provide uniquw username", 400)
        
        if not username:
            return apology("must provide username", 400)

        # Ensure password was submitted
        elif not password:
            return apology("must provide password", 400)

        # Ensure password confirmation are matching
        elif password != confirmation:
            return apology("confirmation must match password", 400)

        # print(check_password_hash(pwhash, password))
        # Insert username and hash to database
        db.execute("INSERT INTO users(username, hash) VALUES (?, ?)", username, pwhash)

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
    user_shares = db.execute("SELECT transactions.stock_id, stocks.symbol, stocks.company_name, sum(transactions.shares) FROM transactions JOIN stocks ON stocks.id = transactions.stock_id WHERE user_id=:user_id GROUP BY stock_id", user_id=user_id)
    
    user_stocks = []

    for stocks in user_shares:
        user_stocks.append(stocks['symbol'])
    
    if request.method == "POST":
        
        stock_to_sell = request.form.get("symbol")
        print('sell', stock_to_sell)
        
    else:
        return render_template("sell.html", user_stocks=user_stocks)


def errorhandler(e):
    """Handle error"""
    if not isinstance(e, HTTPException):
        e = InternalServerError()
    return apology(e.name, e.code)


# Listen for errors
for code in default_exceptions:
    app.errorhandler(code)(errorhandler)
