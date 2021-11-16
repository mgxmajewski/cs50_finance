import os

from cs50 import SQL

# Configure CS50 Library to use SQLite database
path = os.path.dirname(os.path.abspath(__file__))
db_path = os.path.join(path, 'finance_integrated.db')
print(str(db_path))

db = SQL(str('sqlite:///'+db_path))
