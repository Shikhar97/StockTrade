from datetime import datetime as date
from flask import flash
from flask import Blueprint, render_template, request, session, redirect, url_for, jsonify

utility = Blueprint('utility', __name__)
market_time = False


# AJAX Query to update stock prices every 10 seconds
@utility.route("/update_price", methods=["GET"])
def update_content():
    stock_details = config.db_obj.run_query("SELECT * FROM stocks ORDER BY id")
    for row in stock_details:
        if row["curr_price"] > row["prev_curr_price"]:
            row["arrow"] = "arrow_drop_up"
        else:
            row["arrow"] = "arrow_drop_down"
    return jsonify({'html_response': render_template('update_table.html', rows=stock_details)})


# User : when order is placed
@utility.route("/orders/<int:stock_id>", methods=["GET", "POST"])
def place_orders(stock_id):
    if 'loggedin' in session:
        user_id = session['id']
        if request.method == "POST":
            user_data = config.db_obj.run_query('SELECT * FROM user_portfolio WHERE user_id=%s', session['id'])
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
                rows = config.db_obj.run_query('SELECT * FROM stocks WHERE id=%s', stock_id)
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
                    config.db_obj.run_query(update_fund, new_funds, session["id"])
            else:
                stock_data = config.db_obj.run_query('SELECT SUM(quantity) FROM transaction_his WHERE user_id=%s AND '
                                                     'stock_id=%s AND trans_type=%s', session['id'], stock_id, "Buy")
                if stock_data[0]["sum"] is None or quantity > stock_data[0]["sum"]:
                    flash('Not enough shares to sell', category='error')
                    return redirect(url_for('views.orderpage'))
                else:
                    # Updating the funds after selling
                    new_funds = user_data[0]["funds"] + price * quantity
                    update_fund = "UPDATE user_portfolio SET funds=%s WHERE user_id=%s"
                    config.db_obj.run_query(update_fund, new_funds, session["id"])
            if order_type == "Limit":
                order_expiry = date.strptime(request.form.get("expiry"), "%Y-%m-%d")
                config.db_obj.run_query(
                    "INSERT INTO pending_orders "
                    "(stock_id,user_id,order_type,quantity,limit_price,trans_type,expiry_date) "
                    "VALUES (%s,%s,%s,%s,%s,%s,%s)",
                    stock_id, user_id, "Limit", quantity, price, trans_type, order_expiry)
            else:
                config.db_obj.run_query(
                    "INSERT INTO transaction_his (stock_id,user_id,quantity,price, trans_type, order_type) "
                    "VALUES (%s,%s,%s,%s,%s,%s)",
                    stock_id, user_id, quantity, price, trans_type, order_type)

        flash('Orders Placed', category='success')
        return redirect(url_for('views.orderpage'))
    else:
        return render_template("home.html")


# User: Adding funds to buy stocks
@utility.route("/addfunds", methods=["POST", "GET"])
def add_funds():
    if 'loggedin' in session:
        if request.method == "POST":
            user_id = session['id']
            fundsadded = request.form.get('quantity')
            results = config.db_obj.run_query("SELECT * FROM user_portfolio WHERE user_id = %s", user_id)
            for row in results:
                funds = (row['funds'])
                fundsadded = float(fundsadded) + funds
                update_query = "UPDATE user_portfolio SET funds = %s WHERE user_id = %s"
                config.db_obj.run_query(update_query, fundsadded, user_id)
            return redirect(url_for('views.portfolio'))
    return redirect(url_for('views.home'))


# User: Withdraw funds to cash
@utility.route("/withdrawfunds", methods=["POST", "GET"])
def withdraw_funds():
    if 'loggedin' in session:
        if request.method == "POST":
            user_id = session['id']
            amt = request.form.get('quantity')
            results = config.db_obj.run_query("SELECT * FROM user_portfolio WHERE user_id = %s", user_id)
            for row in results:
                funds = (row['funds'])
                funds = funds - float(amt)
                update_query = "UPDATE user_portfolio SET funds = %s WHERE user_id = %s"
                config.db_obj.run_query(update_query, funds, user_id)
            return redirect(url_for('views.portfolio'))
    return redirect(url_for('views.home'))


# User: Modal for buying/selling stocks
@utility.route("/buysell", methods=["POST", "GET"])
def buy_sell():
    stock_details = {}
    if request.method == 'POST':
        stock_id = request.form['id']
        stock_details = config.db_obj.run_query("SELECT * FROM stocks WHERE id = %s", stock_id)
    return jsonify({'htmlresponse': render_template('response.html', stock_details=stock_details)})


# User: Cancel a pending order
@utility.route("/cancelorder/<int:order_id>", methods=["POST", "GET"])
def cancel_pending_order(order_id):
    if "loggedin" in session:
        del_query = "DELETE FROM pending_orders WHERE order_id=%s"
        get_query = "SELECT * FROM pending_orders WHERE order_id=%s"
        output = config.db_obj.run_query(get_query, order_id)
        user_data = config.db_obj.run_query('SELECT * FROM user_portfolio WHERE user_id=%s', output[0]["user_id"])
        new_funds = user_data[0]["funds"] + output[0]["limit_price"] * output[0]["quantity"]
        update_fund = "UPDATE user_portfolio SET funds=%s WHERE user_id=%s"
        config.db_obj.run_query(update_fund, new_funds, output[0]["user_id"])
        config.db_obj.run_query(del_query, order_id)
        return redirect(url_for('views.orderpage'))
    return redirect(url_for('views.home'))


# AJAX query to check market hours
@utility.route("/markettimecheck", methods=["GET"])
def check_market_time():
    if 'loggedin' in session:
        global market_time
        today_day = date.today().strftime("%A")
        output = config.db_obj.run_query("SELECT * FROM market_hour WHERE day_name=%s", today_day)
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
@utility.route("/editmarkettime", methods=["POST", "GET"])
def market_hours():
    if 'loggedin' in session:
        if request.method == "POST":
            day = request.form.get('day')
            from_time = request.form.get('from_time')
            to_time = request.form.get('to_time')
            update_query = "UPDATE market_hour SET from_time = %s, to_time = %s WHERE day_name = %s"
            config.db_obj.run_query(update_query, from_time, to_time, day)
    return redirect(url_for('views.adminhome'))
