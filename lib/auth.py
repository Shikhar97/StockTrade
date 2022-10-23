from werkzeug.security import generate_password_hash, check_password_hash
from flask import Blueprint, render_template, request, flash, redirect, url_for, session

auth = Blueprint('auth', __name__)


# Login page
@auth.route('/login', methods=['GET', 'POST'])
def login():
    # Check if "username" and "password" POST requests exist (user submitted form)
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form['password1']
        # Check if account exists using MySQL
        user = config.db_obj.run_query('SELECT * FROM users WHERE email = %s', email)
        admin = config.db_obj.run_query('SELECT * FROM admin_users WHERE email = %s', email)
        # Fetch one record and return result
        if user:
            password_rs = user[0]['password']
            # If account exists in users table in out database
            if check_password_hash(password_rs, password):
                # Create session data, we can access this data in other routes
                session['loggedin'] = True
                session['id'] = user[0]['id']
                session['email'] = user[0]['email']
                # Redirect to home page
                return redirect(url_for('views.home'))
            else:
                # Account doesn't exist or username/password incorrect
                flash('Incorrect username/password Please try again', category='error')
        elif admin:
            password_rs = admin[0]['password']
            # If account exists in users table in out database
            if check_password_hash(password_rs, password):
                # Create session data, we can access this data in other routes
                session['loggedin'] = True
                session['id'] = admin[0]['id']
                session['email'] = admin[0]['email']
                # Redirect to home page
                return redirect(url_for('views.adminhome'))
            else:
                # Account doesn't exist or username/password incorrect
                flash('Incorrect username/password Please try again', category='error')

        else:
            flash('Email does not exist!', category='error')

    return render_template("login.html")


@auth.route('/logout')
def logout():
    # Remove session data, this will log the user out
    session.clear()
    return redirect(url_for('auth.login'))


@auth.route('/sign-up', methods=['GET', 'POST'])
def sign_up():
    if request.method == 'POST':
        # Create variables for easy access
        name = request.form.get('name')
        password1 = request.form.get('password1')
        password2 = request.form.get('password2')
        email = request.form.get('email')
        account_type = request.form.get('accountType')
        account_type = str(account_type)
        _hashed_password = generate_password_hash(password1)

        # Check if account exists using MySQL
        usercheck = config.db_obj.run_query('SELECT * FROM users WHERE email = %s', email)
        admincheck = config.db_obj.run_query('SELECT * FROM admin_users WHERE email = %s', email)
        print(usercheck, admincheck)
        if usercheck:
            flash('User already exists.', category='error')
        elif admincheck:
            flash('Admin already registered.', category='error')
        elif len(email) < 4:
            flash('Email must be greater than 3 characters.', category='error')
        if len(name) < 2:
            flash('First name must be greater than 1 character.', category='error')
        elif password1 != password2:
            flash('Passwords don\'t match.', category='error')
        elif len(password1) < 7:
            flash('Password must be at least 7 characters.', category='error')
        else:
            if (account_type == "User"):
                # Account doesn't exist and the form data is valid, now insert new account into users table
                config.db_obj.run_query("INSERT INTO users (username, password, email) VALUES (%s,%s,%s)",
                                        name, _hashed_password, email)
                flash('You have successfully registered!', category='success')
                return redirect(url_for('views.home'))
            else:
                config.db_obj.run_query("INSERT INTO admin_users (username, password, email) VALUES (%s,%s,%s)",
                                        name, _hashed_password, email)
                flash('You have successfully registered!', category='success')
                return redirect(url_for('views.adminhome'))

    return render_template("sign_up.html")


@auth.route('/admin', methods=['GET', 'POST'])
def admin():
    # Check if "username" and "password" POST requests exist (user submitted form)
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password1')
        user = config.db_obj.run_query('SELECT * FROM users WHERE email = %s', email)
        # Fetch one record and return result
        if user:
            password_rs = user[0]['password']
            print(password_rs)
            # If account exists in users table in out database
            if check_password_hash(password_rs, password):
                # Create session data, we can access this data in other routes
                session['loggedin'] = True
                session['id'] = user[0]['id']
                session['email'] = user[0]['email']
                # Redirect to home page
                return redirect(url_for('views.adminhome'))
            else:
                # Account doesn't exist or username/password incorrect
                flash('Incorrect username/password Please try again', category='error')
        else:
            flash('Email does not exist!', category='error')

    return render_template("admin.html")
