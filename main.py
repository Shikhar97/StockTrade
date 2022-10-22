from flask import Flask
from lib.views import views
from lib.auth import auth
from lib.stock_ticker import StockList
from flask_session import Session
from apscheduler.schedulers.background import BackgroundScheduler
from lib.db import DB


def setup_stock_updater():
    db_obj = DB("admin", "admin", "stock_trade")
    s_t = StockList(db_obj)
    s_t.initialize_db()
    sched = BackgroundScheduler()
    sched.add_job(s_t.update_price, 'interval', seconds=60)
    sched.start()
    return sched


def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = 'secret_101$'
    app.config["SESSION_PERMANENT"] = False
    app.config["SESSION_TYPE"] = "filesystem"
    Session(app)

    app.register_blueprint(views, url_prefix='/')
    app.register_blueprint(auth, url_prefix='/')

    return app


if __name__ == '__main__':
    app = create_app()
    scheduler = setup_stock_updater()
    app.run(port=5000, debug=True)
    scheduler.shutdown()


 
