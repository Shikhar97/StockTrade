from flask import Blueprint,render_template,request,session,redirect, url_for
from flask_login import login_user, login_required, logout_user, current_user
import psycopg2 
import psycopg2.extras

views=Blueprint('views',__name__)
DB_HOST = "localhost"
DB_NAME = "mydatabase"
DB_USER = "postgres"
DB_PASS = "admin"
    
conn = psycopg2.connect(dbname=DB_NAME, user=DB_USER, password=DB_PASS, host=DB_HOST)

@views.route('/')
def home():    
    # Check if user is loggedin
    cursor = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    if 'loggedin' in session:    
        # User is loggedin show them the home page
        cursor.execute('SELECT * FROM stocks')
        rows = cursor.fetchall()
        # return render_template('home.html', username=session['username'])
        return render_template("home.html", rows=rows)
    return render_template("base.html")


@views.route('/adminhome',methods=["GET", "POST"], endpoint='adminhome')
def adminhome(): 
    cursor = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    cursor.execute('SELECT * FROM stocks')
    rows = cursor.fetchall()
    # Check if user is loggedin
    if 'loggedin' in session:   
        if request.method == "POST":
            name = request.form.get('stock_name')
            price = request.form.get('stock_price')
            cursor.execute("INSERT INTO stocks (stock_name,stock_price) VALUES (%s,%s)", (name, price))
            conn.commit()
            cursor.execute('SELECT * FROM stocks')
            rows = cursor.fetchall()
            # cursor.execute("INSERT INTO stocks (stock_name,stock_price) VALUES (%s,%s)")

        # User is loggedin show them the home page
        # return render_template('home.html', username=session['username'])
            return render_template("admin_home.html", message="Stock added successfully", rows=rows)
        return render_template("admin_home.html",rows=rows)
    else:
        return render_template("home.html")

    # User is not loggedin redirect to login page
    # return redirect(url_for('auth.login'))   
    
    # rows = Stocks.query.all()
    # if request.method == "POST":
    #     name = request.form.get("stock_name")
    #     price = request.form.get("stock_price")
    #     stock = Stocks(stock_name=name,stock_price=price)
    #     db.session.add(stock)	
    #     db.session.commit()
    #     rows = Stocks.query.all()

         
    #     return render_template("admin_home.html",  message="Product added", user=current_user, rows=rows)
    # return render_template("home.html") 




#when edit product option is selected this function is loaded
@views.route("/edit/<int:stock_id>", methods=["GET", "POST"], endpoint='edit')
def edit(stock_id):
    cursor = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    cursor.execute('SELECT * FROM stocks WHERE stock_id = %s', (stock_id,))
    
    # Check if user is loggedin
    if 'loggedin' in session:   
        result = cursor.fetchone()
        if request.method == "POST":
            name = request.form.get("stock_name")
            price = request.form.get("stock_price")
            # cursor.execute('UPDATE stocks SET stock_name = %s, stock_price = %s WHERE stock_id = %s, (name,price,result.stock_id,)')
            sql = "UPDATE stocks SET stock_name = %s, stock_price = %s WHERE stock_id = %s"
            val = (name, price, stock_id)

            cursor.execute(sql, val)
   
            conn.commit()
            cursor.execute('SELECT * FROM stocks')
            rows = cursor.fetchall()
            return render_template("admin_home.html", rows=rows, message="Product edited")
    


    
    # result = Stocks.query.filter_by(stock_id = stock_id).first()
    # if request.method == "POST":
    #     name = request.form.get("stock_name")
    #     price = request.form.get("stock_price")

    #     result.stock_name = name
    #     result.stock_price = price
    #     db.session.commit()
    #     rows = Stocks.query.all()
    #     return render_template("admin_home.html", rows=rows, message="Product edited", user=current_user)

    return render_template("edit.html",result=result)
		


    
	