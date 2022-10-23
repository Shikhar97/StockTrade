from datetime import datetime as date
from faulthandler import disable
from flask import flash
from flask import Blueprint, render_template, request, session, redirect, url_for, jsonify
from lib.db import DB

views = Blueprint('views', __name__)

DB_NAME = "stock_trade"
DB_USER = "admin"
DB_PASS = "admin"
db_obj = DB(DB_USER, DB_PASS, DB_NAME)

market_time = False


# User : Home page
@views.route('/')
def home():
    # Check if user is loggedin
    if 'loggedin' in session:
        # If User is Logged-in show them the home page
        rows = db_obj.run_query('SELECT * FROM stocks ORDER BY id ASC')
        for row in rows:
            if row["curr_price"] > row["prev_curr_price"]:
                row["arrow"] = "arrow_drop_up"
            else:
                row["arrow"] = "arrow_drop_down"
        return render_template("home.html", rows=rows, disable=disable)
    return redirect(url_for('auth.login'))


# AJAX Query to update stock prices every 10 seconds
@views.route("/update_price", methods=["GET"])
def update_content():
    stock_details = db_obj.run_query("SELECT * FROM stocks ORDER BY id")
    for row in stock_details:
        if row["curr_price"] > row["prev_curr_price"]:
            row["arrow"] = "arrow_drop_up"
        else:
            row["arrow"] = "arrow_drop_down"
    return jsonify({'html_response': render_template('update_table.html', rows=stock_details)})


# Admin : Create new stocks
@views.route('/adminhome', methods=["GET", "POST"], endpoint='adminhome')
def adminhome():
    # Check if admin is loggedin
    if 'loggedin' in session:
        if request.method == "POST":
            name = request.form.get('stock_name')
            price = request.form.get('stock_price')
            symbol = request.form.get('stock_symbol')
            volume = request.form.get('stock_volume')
            db_obj.run_query("INSERT INTO stocks (symbol,stock_name,curr_price,volume) VALUES (%s,%s,%s,%s)", symbol,
                             name, price, volume)
        return render_template("admin_home.html")
    else:
        return redirect(url_for('auth.login'))


# User : when order is placed
@views.route("/orders/<int:stock_id>", methods=["GET", "POST"])
def orders(stock_id):
    if 'loggedin' in session:
        user_id = session['id']
        if request.method == "POST":
            user_data = db_obj.run_query('SELECT * FROM user_portfolio WHERE user_id=%s', session['id'])
            if request.form.get('quantity') == "":
                flash("Please choose a quantity", category="error")
                return redirect(url_for('views.orderpage'))
            quantity = float(request.form.get('quantity'))
            trans_type = request.form.get("trans_type")
            order_type = request.form.get("order_type")
            if trans_type is None:
                flash("Please choose Buy/Sell", category="error")
                return redirect(url_for('views.orderpage'))
            elif order_type is None:
                flash("Please choose Limit/Market order", category="error")
                return redirect(url_for('views.orderpage'))

            if request.form.get('price') == "":
                rows = db_obj.run_query('SELECT * FROM stocks WHERE id=%s', stock_id)
                price = rows[0]["curr_price"]
            else:
                price = float(request.form.get('price'))
            if trans_type == "Buy":
                if price * quantity > user_data[0]["funds"]:
                    flash('Not enough funds', category='error')
                    return redirect(url_for('views.orderpage'))
                else:
                    # Updating the funds after the purchase
                    new_funds = user_data[0]["funds"] - price * quantity
                    update_fund = "UPDATE user_portfolio SET funds=%s WHERE user_id=%s"
                    db_obj.run_query(update_fund, new_funds, session["id"])
            else:
                stock_data = db_obj.run_query('SELECT SUM(quantity) FROM transaction_his WHERE user_id=%s AND '
                                              'stock_id=%s AND trans_type=%s', session['id'], stock_id, "Buy")
                if stock_data[0]["sum"] is None or quantity > stock_data[0]["sum"]:
                    flash('Not enough shares to sell', category='error')
                    return redirect(url_for('views.orderpage'))
                else:
                    # Updating the funds after selling
                    new_funds = user_data[0]["funds"] + price * quantity
                    update_fund = "UPDATE user_portfolio SET funds=%s WHERE user_id=%s"
                    db_obj.run_query(update_fund, new_funds, session["id"])
            if order_type == "Limit":
                order_expiry = date.strptime(request.form.get("expiry"), "%Y-%m-%d")
                db_obj.run_query(
                    "INSERT INTO pending_orders "
                    "(stock_id,user_id,order_type,quantity,limit_price,trans_type,expiry_date) "
                    "VALUES (%s,%s,%s,%s,%s,%s,%s)",
                    stock_id, user_id, "Limit", quantity, price, trans_type, order_expiry)
            else:
                db_obj.run_query(
                    "INSERT INTO transaction_his (stock_id,user_id,quantity,price, trans_type, order_type) "
                    "VALUES (%s,%s,%s,%s,%s,%s)",
                    stock_id, user_id, quantity, price, trans_type, order_type)

        flash('Orders Placed', category='success')
        return redirect(url_for('views.orderpage'))
    else:
        return render_template("home.html")


# User : Portfolio has info about cash, funds etc.
@views.route("/portfolio", methods=["POST", "GET"])
def portfolio():
    if 'loggedin' in session:
        invested_value = 0
        current_value = 0
        get_query = "SELECT * FROM transaction_his WHERE user_id=%s"
        output = db_obj.run_query(get_query, session["id"])
        for order in output:
            if order["trans_type"] == "Buy":
                invested_value += order["price"] * order["quantity"]
            else:
                invested_value -= order["price"] * order["quantity"]
        update_query = "UPDATE user_portfolio SET invested_value=%s WHERE user_id=%s"
        db_obj.run_query(update_query, round(invested_value, 2), session["id"])
        fund = db_obj.run_query("SELECT * FROM user_portfolio WHERE user_id=%s", session["id"])
        stock_rows = db_obj.run_query('SELECT * FROM stocks ORDER BY id ASC')
        stock_data = "SELECT symbol, SUM(case when trans_type='Buy' then quantity else - quantity end) as stock_count " \
                     "FROM transaction_his  INNER JOIN stocks on stocks.id = transaction_his.stock_id " \
                     "WHERE user_id =%s GROUP BY symbol"
        stock_list_output = db_obj.run_query(stock_data, session["id"])
        for user_stock in stock_list_output:
            value = db_obj.run_query("SELECT curr_price FROM stocks WHERE symbol=%s", user_stock["symbol"])
            current_value += value[0]["curr_price"] * user_stock["stock_count"]
        return render_template("portfolio.html", funds=round(fund[0]["funds"], 2), stock_rows=stock_rows,
                               invested_value=fund[0]["invested_value"], curr_value=current_value,
                               stock_info=stock_list_output)
    return redirect(url_for('views.home'))


# User: Pending orders and transaction history
@views.route("/orderpage", methods=["POST", "GET"])
def orderpage():
    if 'loggedin' in session:
        user_id = session['id']
        transac_rows = "SELECT * " \
                       "FROM stocks INNER JOIN transaction_his ON stocks.id = transaction_his.stock_id " \
                       "WHERE transaction_his.user_id = %s ORDER BY order_id DESC"
        rows = db_obj.run_query(transac_rows, user_id)
        stock_rows = db_obj.run_query('SELECT * FROM stocks ORDER BY id ASC')
        pending_rows = db_obj.run_query("SELECT * FROM stocks "
                                        "INNER JOIN pending_orders ON stocks.id = pending_orders.stock_id "
                                        "WHERE pending_orders.user_id = %s ORDER BY order_id DESC", user_id)
        return render_template("orders.html", rows=rows, stock_rows=stock_rows, pending_orders=pending_rows)
    return redirect(url_for('views.home'))


# User: Adding funds to buy stocks
@views.route("/addfunds", methods=["POST", "GET"])
def addfunds():
    if 'loggedin' in session:
        if request.method == "POST":
            user_id = session['id']
            fundsadded = request.form.get('quantity')
            results = db_obj.run_query("SELECT * FROM user_portfolio WHERE user_id = %s", user_id)
            for row in results:
                funds = (row['funds'])
                fundsadded = float(fundsadded) + funds
                update_query = "UPDATE user_portfolio SET funds = %s WHERE user_id = %s"
                db_obj.run_query(update_query, fundsadded, user_id)
            return redirect(url_for('views.portfolio'))
    return redirect(url_for('views.home'))


# User: Withdraw funds to cash
@views.route("/withdrawfunds", methods=["POST", "GET"])
def withdrawfunds():
    if 'loggedin' in session:
        if request.method == "POST":
            user_id = session['id']
            amt = request.form.get('quantity')
            results = db_obj.run_query("SELECT * FROM user_portfolio WHERE user_id = %s", user_id)
            for row in results:
                funds = (row['funds'])
                funds = funds - float(amt)
                update_query = "UPDATE user_portfolio SET funds = %s WHERE user_id = %s"
                db_obj.run_query(update_query, funds, user_id)
            return redirect(url_for('views.portfolio'))
    return redirect(url_for('views.home'))


# User: Modal for buying/selling stocks
@views.route("/buysell", methods=["POST", "GET"])
def ajaxfile():
    stock_details = {}
    if request.method == 'POST':
        stock_id = request.form['id']
        stock_details = db_obj.run_query("SELECT * FROM stocks WHERE id = %s", stock_id)
    return jsonify({'htmlresponse': render_template('response.html', stock_details=stock_details)})


# User: Cancel a pending order
@views.route("/cancelorder/<int:order_id>", methods=["POST", "GET"])
def cancel_pending_order(order_id):
    if "loggedin" in session:
        del_query = "DELETE FROM pending_orders WHERE order_id=%s"
        get_query = "SELECT * FROM pending_orders WHERE order_id=%s"
        output = db_obj.run_query(get_query, order_id)
        user_data = db_obj.run_query('SELECT * FROM user_portfolio WHERE user_id=%s', output[0]["user_id"])
        new_funds = user_data[0]["funds"] + output[0]["limit_price"] * output[0]["quantity"]
        update_fund = "UPDATE user_portfolio SET funds=%s WHERE user_id=%s"
        db_obj.run_query(update_fund, new_funds, output[0]["user_id"])
        db_obj.run_query(del_query, order_id)
        return redirect(url_for('views.orderpage'))
    return redirect(url_for('views.home'))


# AJAX query to check market hours
@views.route("/markettimecheck", methods=["GET"])
def check_market_time():
    if 'loggedin' in session:
        global market_time
        today_day = date.today().strftime("%A")
        output = db_obj.run_query("SELECT * FROM market_hour WHERE day_name=%s", today_day)
        current_time = date.now().strftime("%H:%M")
        for row in output:
            to_time = row['to_time'].strftime('%H:%M')
            from_time = row['from_time'].strftime('%H:%M')
            d1 = date.strptime(current_time, '%H:%M')
            d2 = date.strptime(from_time, '%H:%M')
            d3 = date.strptime(to_time, '%H:%M')
            if (d2 < d1 < d3) or (d2 > d1 > d3):
                market_time = True
            else:
                market_time = True
        return jsonify({'market_time': market_time})


# Admin: edits market hours
@views.route("/editmarkettime", methods=["POST", "GET"])
def market_hours():
    if 'loggedin' in session:
        if request.method == "POST":
            day = request.form.get('day')
            from_time = request.form.get('from_time')
            to_time = request.form.get('to_time')
            update_query = "UPDATE market_hour SET from_time = %s, to_time = %s WHERE day_name = %s"
            db_obj.run_query(update_query, from_time, to_time, day)
    return redirect(url_for('views.adminhome'))
