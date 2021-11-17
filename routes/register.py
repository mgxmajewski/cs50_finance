from flask import render_template, request, redirect
from db_connection import db
from helpers import apology
from werkzeug.security import generate_password_hash
from . import routes


@routes.route("/register", methods=["GET", "POST"])
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