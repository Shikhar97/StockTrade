from decimal import Decimal
from genericpath import exists
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
    # db_obj.run_query('SELECT * FROM stocks WHERE stock_id = %s', (stock_id,))
    # db_obj.run_query('SELECT * FROM stocks')
    # rows = cursor.fetchall()
    # Check if user is loggedin
    if 'loggedin' in session:
        if request.method == "POST":
            quantity = request.form.get('quantity')
            price = request.form.get('price')
            user_id = session['id']
            db_obj.run_query("INSERT INTO transaction_his (stock_id,user_id,quantity,price) VALUES (%s,%s,%s,%s)",
                             stock_id, user_id, quantity, price)

            return redirect(url_for('views.orderpage'))

        else:
            rows = db_obj.run_query('SELECT * FROM stocks ORDER BY id ASC')
            return render_template("orders.html", rows=rows)
    else:
        return render_template("home.html")


@views.route("/portfolio", methods=["POST", "GET"])
def portfolio():
    if 'loggedin' in session:
        user_id = session['id']
        rows = db_obj.run_query("SELECT * FROM user_portfolio WHERE user_id = %s", user_id)
        # for row in rows:
        #     funds = (row['funds'])
        return render_template("portfolio.html", rows=rows)
    return redirect(url_for('views.home'))


@views.route("/orderpage", methods=["POST", "GET"])
def orderpage():
    if 'loggedin' in session:
        user_id = session['id']
        sql = "SELECT stocks.stock_name, stocks.curr_price, transaction_his.quantity, transaction_his.price " \
              "FROM stocks INNER JOIN transaction_his ON stocks.id = transaction_his.stock_id " \
              "WHERE transaction_his.user_id = %s ORDER BY order_id DESC"
        rows = db_obj.run_query(sql, user_id)
        stock_rows = db_obj.run_query('SELECT * FROM stocks ORDER BY id ASC')
        return render_template("orders.html", rows=rows, stock_rows=stock_rows)
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
