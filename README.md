# C$50 Finance

Finance is one of CS50's course assignments. It is a web app via which you can manage portfolios of stocks. Not only
will this tool allow you to check real stocks’ actual prices and portfolios’ values, but it will also let you buy (okay,
“buy”) and sell (okay, “sell”) stocks by querying IEX for stocks’ prices.

My personal touch to the application was to add a lookup functionality for stock names. Using ETL software (Talend
Studio), I fetched 10k rows of stock data and uploaded it to applications SQLite DB. I have also created an API **
suggestions** endpoint. The data, is retrieved with dedicated JS script, which fetches the five best matches for the
lookup phrase on each user keystroke.

Designing a DB from the scratch, was another interesting part of the project. To achieve clean architecture, I followed
the database normalization process to.

### Specification

<p><b><i>register</i></b></p>
    <ul>
      <li>
        requires that a user input a username implemented as a text field whose name is username. Render an apology if
        the user’s input is blank or the username already exists
      </li>
      <li>
        requires that a user input a password, implemented as a text field whose name is password, and then that same
        password again implemented as a text field whose name is confirmation. Render an apology if either input is
        blank or the passwords do not match
      </li>
      <li>
        submits the user’s input via POST to /register
      </li>
      <li>
        inserts the new user into users, storing a hash of the user’s password, not the password itself. Hash the user’s
        password with generate_password_hash Odds are you’ll want to create a new template (e.g., register.html) that’s
        quite similar to login.html
      </li>
    </ul>
    <p><b><i>quote</i></b></p>
    <ul>
      <li>
        require that a user input a stock’s symbol, implemented as a text field whose name is symbol
      </li>
      <li>
        submit the user’s input via POST to /quote
      </li>
    </ul>
    <p><b><i>buy</i></b></p>
    <ul>
      <li>
        requires that a user input a stock’s symbol, implemented as a text field whose name is symbol. Render an apology
        if the input is blank or the symbol does not exist (as per the return value of lookup)
      </li>
      <li>
        requires that a user input a number of shares, implemented as a field whose name is shares. Render an apology if
        the input is not a positive integer
      </li>
      <li>
        submits the user’s input via POST to /buy
      </li>
      <li>
        adds one or more new tables to finance.db via which to keep track of the purchase.
      </li>
      <li>
        renders an apology, without completing a purchase, if the user cannot afford the number of shares at the
        current price
      </li>
    </ul>
    <p><b><i>index</i></b></p>
    <p>
      Displays an HTML table summarizing, for the user currently logged in, which stocks the user owns, the numbers of
      shares owned, the current price of each stock, and the total value of each holding (i.e., shares times price).
      Also display the user’s current cash balance along with a grand total (i.e., stocks’ total value plus cash).
    </p>
    <p><b><i>sell</i></b></p>
    <ul>
      <li>requires that a user input a stock’s symbol, implemented as a select menu whose name is symbol. Render an
        apology if the user fails to select a stock or if (somehow, once submitted) the user does not own any shares of
        that stock
      </li>
      <li>requires that a user input a number of shares, implemented as a field whose name is shares. Render an apology
        if the input is not a positive integer or if the user does not own that many shares of the stock
      </li>
      <li>submits the user’s input via POST to /sell</li>
    </ul>
    <p><b><i>history</i></b></p>
    <ul>
      <li>
        displays an HTML table summarizing all of a user’s transactions ever, listing row by row each and every buy and
        every sell
      </li>
      <li>
        Each row informs a stock was bought or sold and includes the stock’s symbol, the (purchase or sale) price, the
        number of shares bought or sold, and the date and time at which the transaction occurred.
      </li>
</ul>