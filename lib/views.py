import datetime
from flask import flash
from flask import Blueprint, render_template, request, session, redirect, url_for, jsonify
from lib.db import DB

views = Blueprint('views', __name__)

DB_NAME = "stock_trade"
DB_USER = "admin"
DB_PASS = "admin"
db_obj = DB(DB_USER, DB_PASS, DB_NAME)


@views.route('/')
def home():
    # Check if user is loggedin
    if 'loggedin' in session:
        # User is Logged-in show them the home page
        print("logged in on home page")
        rows = db_obj.run_query('SELECT * FROM stocks ORDER BY id ASC')
        return render_template("home.html", rows=rows)
    return redirect(url_for('auth.login'))


@views.route('/adminhome', methods=["GET", "POST"], endpoint='adminhome')
def adminhome():
    rows = db_obj.run_query('SELECT * FROM stocks')
    # Check if user is loggedin
    if 'loggedin' in session:
        if request.method == "POST":
            name = request.form.get('stock_name')
            price = request.form.get('stock_price')
            db_obj.run_query("INSERT INTO stocks (stock_name,curr_price) VALUES (%s,%s)", name, price)
            rows = db_obj.run_query('SELECT * FROM stocks')
            return render_template("admin_home.html", message="Stock added successfully", rows=rows)
        return render_template("admin_home.html", rows=rows)
    else:
        return redirect(url_for('auth.login'))


# when edit product option is selected this function is loaded
@views.route("/edit/<int:stock_id>", methods=["GET", "POST"], endpoint='edit')
def edit(stock_id):
    result = {}
    # Check if user is loggedin
    if 'loggedin' in session:
        # result = db_obj.run_query('SELECT * FROM stocks WHERE id = %s', stock_id)
        if request.method == "POST":
            name = request.form.get("stock_name")
            price = request.form.get("stock_price")
            update_query = "UPDATE stocks SET stock_name = %s, curr_price = %s WHERE id = %s"
            db_obj.run_query(update_query, name, price, stock_id)
            rows = db_obj.run_query('SELECT * FROM stocks')
            return render_template("admin_home.html", rows=rows, message="Product edited")

    return redirect(url_for('views.adminhome'))


# when edit product option is selected this function is loaded
@views.route("/orders/<int:stock_id>", methods=["GET", "POST"])
def orders(stock_id):
    if 'loggedin' in session:
        user_id = session['id']
        if request.method == "POST":
            user_data = db_obj.run_query('SELECT * FROM user_portfolio WHERE user_id=%s', session['id'])
            quantity = float(request.form.get('quantity'))
            if request.form.get('price') == "":
                rows = db_obj.run_query('SELECT * FROM stocks WHERE id=%s', stock_id)
                price = rows[0]["curr_price"]
            else:
                price = float(request.form.get('price'))
            trans_type = request.form.get("trans_type")
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

            order_type = request.form.get("order_type")

            if order_type == "Limit":
                order_expiry = datetime.datetime.strptime(request.form.get("expiry"), "%Y-%m-%d")
                db_obj.run_query(
                    "INSERT INTO pending_orders (stock_id,user_id,quantity,limit_price, trans_type, expiry_date) "
                    "VALUES (%s,%s,%s,%s,%s,%s)",
                    stock_id, user_id, quantity, price, trans_type, order_expiry)
            else:
                db_obj.run_query(
                    "INSERT INTO transaction_his (stock_id,user_id,quantity,price, trans_type, order_type) "
                    "VALUES (%s,%s,%s,%s,%s,%s)",
                    stock_id, user_id, quantity, price, trans_type, order_type)

            return redirect(url_for('views.orderpage'))

        else:
            transaction_rows = db_obj.run_query('SELECT * FROM transaction_his')
            pending_rows = db_obj.run_query('SELECT * FROM pending_orders')
            stock_rows = db_obj.run_query('SELECT * FROM stocks ORDER BY id ASC')
            return render_template("orders.html", rows=transaction_rows, stock_rows=stock_rows,
                                   pending_orders=pending_rows)
    else:
        return render_template("home.html")


@views.route("/portfolio", methods=["POST", "GET"])
def portfolio():
    if 'loggedin' in session:
        invested_value = 0
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
        return render_template("portfolio.html", funds=round(fund[0]["funds"],2), stock_rows=stock_rows)
    return redirect(url_for('views.home'))


@views.route("/orderpage", methods=["POST", "GET"])
def orderpage():
    if 'loggedin' in session:
        user_id = session['id']
        sql = "SELECT * " \
              "FROM stocks INNER JOIN transaction_his ON stocks.id = transaction_his.stock_id " \
              "WHERE transaction_his.user_id = %s ORDER BY order_id DESC"
        rows = db_obj.run_query(sql, user_id)
        stock_rows = db_obj.run_query('SELECT * FROM stocks ORDER BY id ASC')
        pending_rows = db_obj.run_query('SELECT * FROM pending_orders')
        return render_template("orders.html", rows=rows, stock_rows=stock_rows, pending_orders=pending_rows)
    return redirect(url_for('views.home'))


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
                # print(fundsadded)
                # print(type(fundsadded))
                update_query = "UPDATE user_portfolio SET funds = %s WHERE user_id = %s"
                db_obj.run_query(update_query, fundsadded, user_id)
            return redirect(url_for('views.portfolio'))
    return redirect(url_for('views.home'))


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
                # print(fundsadded)
                # print(type(fundsadded))
                update_query = "UPDATE user_portfolio SET funds = %s WHERE user_id = %s"
                db_obj.run_query(update_query, funds, user_id)
            return redirect(url_for('views.portfolio'))
    return redirect(url_for('views.home'))


@views.route("/buysell", methods=["POST", "GET"])
def ajaxfile():
    stock_details = {}
    if request.method == 'POST':
        stock_id = request.form['id']
        stock_details = db_obj.run_query("SELECT * FROM stocks WHERE id = %s", stock_id)
    return jsonify({'htmlresponse': render_template('response.html', stock_details=stock_details)})


@views.route("/edit", methods=["POST", "GET"])
def ajaxfileedit():
    rows = {}
    if request.method == 'POST':
        stock_id = request.form['id']
        rows = db_obj.run_query("SELECT * FROM stocks WHERE id = %s", stock_id)
    return jsonify({'htmlresponse': render_template('edit.html', rows=rows)})
