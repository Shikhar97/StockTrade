from faulthandler import disable
from flask import Blueprint, render_template, request, session, redirect, url_for

views = Blueprint('views', __name__)
market_time = False


# User : Home page
@views.route('/')
def home():
    # Check if user is loggedin
    if 'loggedin' in session:
        # If User is Logged-in show them the home page
        rows = config.db_obj.run_query('SELECT * FROM stocks ORDER BY id ASC')
        for row in rows:
            if row["curr_price"] < row["prev_curr_price"]:
                row["arrow"] = "arrow_drop_up"
            else:
                row["arrow"] = "arrow_drop_down"
        return render_template("home.html", rows=rows, username=session['username'])
    return redirect(url_for('auth.login'))


# Admin : Create new stocks
@views.route('/adminhome', methods=["GET", "POST"], endpoint='adminhome')
def admin_home():
    # Check if admin is logged in
    if 'loggedin' in session:
        if request.method == "POST":
            name = request.form.get('stock_name')
            price = request.form.get('stock_price')
            symbol = request.form.get('stock_symbol')
            volume = request.form.get('stock_volume')
            config.db_obj.run_query("INSERT INTO stocks (symbol,stock_name,curr_price,volume) VALUES (%s,%s,%s,%s)",
                                    symbol,
                                    name, price, volume)
        return render_template("admin_home.html", username=session['username'])
    else:
        return redirect(url_for('auth.login'))


# User : Portfolio has info about cash, funds etc.
@views.route("/portfolio", methods=["POST", "GET"])
def portfolio():
    if 'loggedin' in session:
        invested_value = 0
        current_value = 0
        get_query = "SELECT * FROM transaction_his WHERE user_id=%s"
        output = config.db_obj.run_query(get_query, session["id"])
        for order in output:
            if order["trans_type"] == "Buy":
                invested_value += order["price"] * order["quantity"]
            else:
                invested_value -= order["price"] * order["quantity"]
        update_query = "UPDATE user_portfolio SET invested_value=%s WHERE user_id=%s"
        config.db_obj.run_query(update_query, round(invested_value, 2), session["id"])
        fund = config.db_obj.run_query("SELECT * FROM user_portfolio WHERE user_id=%s", session["id"])
        stock_rows = config.db_obj.run_query('SELECT * FROM stocks ORDER BY id ASC')
        for row in stock_rows:
            if row["curr_price"] < row["prev_curr_price"]:
                row["arrow"] = "arrow_drop_up"
            else:
                row["arrow"] = "arrow_drop_down"
        stock_data = "SELECT symbol, SUM(case when trans_type='Buy' then quantity else - quantity end) as stock_count " \
                     "FROM transaction_his  INNER JOIN stocks on stocks.id = transaction_his.stock_id " \
                     "WHERE user_id =%s GROUP BY symbol"
        stock_list_output = config.db_obj.run_query(stock_data, session["id"])
        for user_stock in stock_list_output:
            value = config.db_obj.run_query("SELECT curr_price FROM stocks WHERE symbol=%s", user_stock["symbol"])
            current_value += value[0]["curr_price"] * user_stock["stock_count"]
        return render_template("portfolio.html", funds=round(fund[0]["funds"], 2), stock_rows=stock_rows,
                               invested_value=fund[0]["invested_value"], curr_value=float("%.2f" % current_value),
                               stock_info=stock_list_output, username=session['username'])
    return redirect(url_for('views.home'))


# User: Pending orders and transaction history
@views.route("/orderpage", methods=["POST", "GET"])
def orderpage():
    if 'loggedin' in session:
        user_id = session['id']
        transac_rows = "SELECT * " \
                       "FROM stocks INNER JOIN transaction_his ON stocks.id = transaction_his.stock_id " \
                       "WHERE transaction_his.user_id = %s ORDER BY order_id DESC"
        rows = config.db_obj.run_query(transac_rows, user_id)
        stock_rows = config.db_obj.run_query('SELECT * FROM stocks ORDER BY id ASC')
        for row in stock_rows:
            if row["curr_price"] < row["prev_curr_price"]:
                row["arrow"] = "arrow_drop_up"
            else:
                row["arrow"] = "arrow_drop_down"
        pending_rows = config.db_obj.run_query("SELECT * FROM stocks "
                                               "INNER JOIN pending_orders ON stocks.id = pending_orders.stock_id "
                                               "WHERE pending_orders.user_id = %s ORDER BY order_id DESC", user_id)
        return render_template("orders.html", rows=rows, stock_rows=stock_rows, pending_orders=pending_rows,
                               username=session['username'])
    return redirect(url_for('views.home'))
