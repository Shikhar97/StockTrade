from flask import Flask
from lib.views import views
from lib.auth import auth
from lib.stock_ticker import StockList
from apscheduler.schedulers.background import BackgroundScheduler


def setup_stock_updater():
    s_t = StockList()
    s_t.initialize_db()
    sched = BackgroundScheduler()
    sched.add_job(s_t.update_price, 'interval', seconds=60)
    sched.start()
    return sched


def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = 'secret_101$'

    app.register_blueprint(views, url_prefix='/')
    app.register_blueprint(auth, url_prefix='/')

    return app


if __name__ == '__main__':
    # scheduler = setup_stock_updater()
    app = create_app()
    app.run(port=5000, debug=True)
    # scheduler.shutdown()


 
