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
    # cursor.execute('SELECT * FROM stocks')
    # rows = cursor.fetchall()
    if 'loggedin' in session:    
        # User is loggedin show them the home page
        cursor.execute('SELECT * FROM stocks')
        rows = cursor.fetchall()
        # return render_template('home.html', username=session['username'])
        return render_template("home.html",rows=rows)
        # return render_template("rough.html")
    # return render_template("b.html")
    return redirect(url_for('auth.login'))
    # return "<h2>Home<h2/>"


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

    return render_template("edit.html",result=result)


		


#rendering the HTML page which has the button
@views.route('/json')
def json():
    return render_template('json.html')

#background process happening without any refreshing
@views.route('/background_process_test')
def background_process_test():
    print ("Hello")
    return ("nothing")







    
	