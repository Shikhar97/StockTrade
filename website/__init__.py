import imp
from flask import Flask
from os import path
import psycopg2 
import psycopg2.extras



def create_app():
    app= Flask(__name__)
    app.config['SECRET_KEY'] = 'hjshjhdjahjshkjdhjs'
    DB_HOST = "localhost"
    DB_NAME = "mydatabase"
    DB_USER = "postgres"
    DB_PASS = "admin"
    
    conn = psycopg2.connect(dbname=DB_NAME, user=DB_USER, password=DB_PASS, host=DB_HOST)


    from .views import views
    from .auth import auth

    app.register_blueprint(views, url_prefix='/')
    app.register_blueprint(auth, url_prefix='/')

    return app

