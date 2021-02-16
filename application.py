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
    

    quote = lookup('AAPL')
    print(quote)
    iex_symbol = quote['symbol']
    iex_name = quote['name']
    iex_price = usd(quote['price'])
    user_id = session['user_id']
    user_db_import = db.execute("SELECT username FROM users WHERE id = :user_id ", user_id = user_id)
    user_name = user_db_import[0]['username']

    user_stock_list = db.execute("SELECT transactions.stock, stocks.symbol, stocks.company_name, sum(transactions.shares) FROM transactions JOIN stocks ON stocks.id = transactions.stock WHERE buyer=:user_id GROUP BY stock", user_id=user_id)
    
    print(user_stock_list)
    
    for stock in user_stock_list:
        stock_quote = lookup(stock['symbol'])
        stock_actual_price = stock_quote['price']
        stock_total_value = stock['sum(transactions.shares)'] * stock_actual_price
        print(stock_total_value)    
    

    # Redirect user to login
    return render_template("index.html", 
                            iex_symbol=iex_symbol, 
                            iex_name=iex_name, 
                            iex_price=iex_price, 
                            user_name=user_name)



@app.route("/buy", methods=["GET", "POST"])
@login_required
def buy():
    """Buy shares of stock"""

    if request.method == "POST":


        user_id = session['user_id']
        seller_id = db.execute("SELECT id FROM users WHERE username = 'broker' ")[0]['id']
        user_name = db.execute("SELECT username FROM users WHERE id = :user_id ", user_id = user_id)[0]['username']
        balance = db.execute("SELECT cash FROM users WHERE id = :user_id", user_id = user_id)[0]['cash']
        symbol = request.form.get("symbol")
        shares = int(request.form.get("shares"))

        stock_import = lookup(symbol)

        iex_symbol = stock_import['symbol']
        iex_name = stock_import['name']
        iex_price = stock_import['price']

        stock_purchase_value = iex_price * shares

        balance_after_trans = balance - stock_purchase_value

        print(balance_after_trans)
        print(user_id)

        db.execute("INSERT OR IGNORE INTO stocks(symbol, company_name) VALUES (:symbol, :company_name)", symbol=iex_symbol, company_name=iex_name)
        
        
        # Ensure that 
        if  balance >= stock_purchase_value:
            stock_db_id = db.execute("SELECT id FROM stocks WHERE symbol = ?", iex_symbol)[0]['id']
            print(stock_db_id)
            
            db.execute("INSERT INTO transactions (stock, buyer, seller, shares, price) VALUES (?, ?, ?, ?, ?)", stock_db_id, user_id, seller_id, shares, iex_price)
            
            db.execute("UPDATE users SET cash= ? WHERE id= ? ", balance_after_trans, user_id)
        # Ensure order of stock was valid
        
        if not symbol:
            return apology("must provide valid stock name", 403)
        elif symbol == None:
            return apology("Sorry, no such a stock", 403)
        elif balance < stock_purchase_value:
            return apology("Sorry, you dont have enough cash", 403)

        # Redirect user to login
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
        rows = db.execute("SELECT * FROM users WHERE username = ?", request.form.get("username"))

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
            return apology("must provide valid stock name", 403)
        elif quote == None:
            return apology("Sorry, no such a stock", 403)

        print(quote)
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
        conhash = generate_password_hash(confirmation, method='pbkdf2:sha256', salt_length=8)
        # Ensure username was submitted
        if not username:
            return apology("must provide username", 403)

        # Ensure password was submitted
        elif not password:
            return apology("must provide password", 403)

        # Ensure password confirmation are matching
        elif password != confirmation:
            return apology("must match password", 403)

        print(check_password_hash(pwhash, password))
        # Insert username and hash to database
        db.execute("INSERT INTO users(username, hash) VALUES (?, ?)", username, conhash)

        # Redirect user to login
        return redirect("/login")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("register.html")


@app.route("/sell", methods=["GET", "POST"])
@login_required
def sell():
    """Sell shares of stock"""
    return apology("TODO")


def errorhandler(e):
    """Handle error"""
    if not isinstance(e, HTTPException):
        e = InternalServerError()
    return apology(e.name, e.code)


# Listen for errors
for code in default_exceptions:
    app.errorhandler(code)(errorhandler)
