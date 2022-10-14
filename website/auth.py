from flask import Blueprint, render_template, request, flash, redirect, url_for,session
from werkzeug.security import generate_password_hash, check_password_hash
import psycopg2 
import psycopg2.extras

auth = Blueprint('auth', __name__)

DB_HOST = "localhost"
DB_NAME = "mydatabase"
DB_USER = "postgres"
DB_PASS = "admin"
    
conn = psycopg2.connect(dbname=DB_NAME, user=DB_USER, password=DB_PASS, host=DB_HOST)


@auth.route('/login', methods=['GET', 'POST'])
def login():    
    cursor = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    # Check if "username" and "password" POST requests exist (user submitted form)
    if request.method == 'POST' :
        email = request.form.get('email')
        password = request.form['password1']
        print(password)
        # Check if account exists using MySQL
        cursor.execute('SELECT * FROM users WHERE email = %s', (email,))
        # Fetch one record and return result
        user = cursor.fetchone()
        # user=db.session.query(User).filter(User.email==email)

        if user:
            password_rs = user['password']
            print(password_rs)
            # If account exists in users table in out database
            if check_password_hash(password_rs, password):
                # Create session data, we can access this data in other routes
                session['loggedin'] = True
                session['id'] = user['id']
                session['email'] = user['email']
                # Redirect to home page
                return redirect(url_for('views.home'))
            else:
                # Account doesnt exist or username/password incorrect
                flash('Incorrect username/password Please try again', category='error')
        else:
            flash('Email does not exist!',category='error')
    
    return render_template("login.html")


@auth.route('/logout')
def logout():   
   # Remove session data, this will log the user out
   session.pop('loggedin', None)
   session.pop('id', None)
   session.pop('email', None)
   # Redirect to login page
   return redirect(url_for('auth.login'))
    


@auth.route('/sign-up', methods=['GET', 'POST'])
def sign_up():
    cursor = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    if request.method == 'POST' :
        # Create variables for easy access
        name = request.form.get('name')
        password1 = request.form.get('password1')
        password2 = request.form.get('password2')
        email = request.form.get('email')
        print(name)
        print(email)
        print(password1)
        _hashed_password = generate_password_hash(password1)
 
        #Check if account exists using MySQL
        cursor.execute('SELECT * FROM users WHERE email = %s', (email,))
        user = cursor.fetchone()
        print(user)
        if user:
            flash('User already exists.', category='error')
        elif len(email) < 4:
            flash('Email must be greater than 3 characters.', category='error')
        if len(name) < 2:
            flash('First name must be greater than 1 character.', category='error')
        elif password1 != password2:
            flash('Passwords don\'t match.', category='error')
        elif len(password1) < 7:
            flash('Password must be at least 7 characters.', category='error')
        else:
            # Account doesnt exists and the form data is valid, now insert new account into users table
            cursor.execute("INSERT INTO users (email, name, password) VALUES (%s,%s,%s)", (email, name, _hashed_password))
            conn.commit()
            flash('You have successfully registered!', category='success')
            return redirect(url_for('views.home'))
       
    return render_template("sign_up.html")


@auth.route('/admin', methods=['GET', 'POST'])
def admin():  
    cursor = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    # Check if "username" and "password" POST requests exist (user submitted form)
    if request.method == 'POST' :
        email = request.form.get('email')
        password = request.form.get('password1')
        print(password)
        cursor.execute('SELECT * FROM users WHERE email = %s', (email,))
        # Fetch one record and return result
        user = cursor.fetchone()
        if user:
            password_rs = user['password']
            print(password_rs)
            # If account exists in users table in out database
            if check_password_hash(password_rs, password):
                # Create session data, we can access this data in other routes
                session['loggedin'] = True
                session['id'] = user['id']
                session['email'] = user['email']
                # Redirect to home page
                return redirect(url_for('views.adminhome'))
            else:
                # Account doesnt exist or username/password incorrect
                flash('Incorrect username/password Please try again', category='error')
        else:
            flash('Email does not exist!',category='error')
    

   
    return render_template("admin.html")


