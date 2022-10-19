from flask import Flask

from lib.stock_price_updater import UpdateStock
from lib.views import views
from lib.auth import auth
from lib.stock_ticker import StockList
from apscheduler.schedulers.background import BackgroundScheduler

def init_db():
    s_t = StockList()
    s_t.initialize_db()

def setup_stock_updater():
    u_t = UpdateStock()
    scheduler = BackgroundScheduler()
    scheduler.add_job(u_t.update_price, 'interval', seconds=60)
    scheduler.start()
    return scheduler

def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = 'secret_101$'

    app.register_blueprint(views, url_prefix='/')
    app.register_blueprint(auth, url_prefix='/')

    return app


if __name__ == '__main__':
    init_db()
    scheduler = setup_stock_updater()
    app = create_app()
    app.run(port=5000, debug=True)
    scheduler.shutdown()


 
