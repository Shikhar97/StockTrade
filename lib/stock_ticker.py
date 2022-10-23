from datetime import datetime as date
import random

from apscheduler.schedulers.background import BackgroundScheduler
from stocksymbol import StockSymbol


def get_price(init_value, change_factor=0.007):
    return float("{:.2f}".format(
        init_value + change_factor * random.randint(int(((init_value + 1) / 2) * -1), int((init_value + 1) / 2))))


class StockList:
    def __init__(self, db_obj):
        self.api_key = 'ab43c7ee-4009-4e4f-83a4-cf41c59dd486'
        self.ss = StockSymbol(self.api_key)
        self.symbol_list_us = self.ss.get_symbol_list(index="NDX")
        self.db = db_obj
        self.sched = BackgroundScheduler()
        self.sched.add_job(self.schedule_jobs, 'interval', seconds=5)
        self.sched.start()

    def schedule_jobs(self):
        job_list = [job.id for job in self.sched.get_jobs()]
        today_day = date.today().strftime("%A")
        output = self.db.run_query("SELECT * FROM market_hour WHERE day_name=%s", today_day)
        current_time = date.now().strftime("%H:%M")
        to_time = output[0]['to_time'].strftime('%H:%M')
        from_time = output[0]['from_time'].strftime('%H:%M')
        d1 = date.strptime(current_time, '%H:%M')
        d2 = date.strptime(from_time, '%H:%M')
        d3 = date.strptime(to_time, '%H:%M')

        # Update the close price once market is close
        run_date = date.combine(date.today(), date.time(d3))
        self.sched.add_job(self.update_market_close_price, 'date', run_date=run_date, id="market_close")

        # Update the close price once market opens
        run_date = date.combine(date.today(), date.time(d2))
        self.sched.add_job(self.update_market_open_price, 'date', run_date=run_date, id="market_open")

        # Update market prices
        if d2 < d1 < d3:
            if "market_update" not in job_list:
                self.sched.add_job(self.update_price, 'interval', seconds=30, id="market_update")
        else:
            if "market_update" in job_list:
                self.sched.remove_job("market_update")

        if "update_pending_order" not in job_list:
            self.sched.add_job(self.update_pending_order_table, 'interval', seconds=300, id="update_pending_order")
        if "trigger_pending_orders" not in job_list:
            self.sched.add_job(self.trigger_pending_orders, 'interval', seconds=10, id="trigger_pending_orders")
        if d1 > d2 and "market_open" in job_list:
            self.sched.remove_job("market_open")
        elif d1 > d3 and "market_close" in job_list:
            self.sched.remove_job("market_close")
        print(job_list)

    def initialize_db(self):
        for stock in self.symbol_list_us:
            try:
                self.db.run_query("INSERT INTO stocks (symbol, stock_name, volume, curr_price, day_high, day_low) "
                                  "VALUES (%s, %s, %s, %s, -1, 99999)",
                                  stock["symbol"],
                                  stock["longName"],
                                  random.randint(10000, 1000000),
                                  random.randint(10, 1000))
                if "INSERT 0 1" not in self.db.cursor.statusmessage:
                    print("Cannot insert")
            except Exception as e:
                if "already exists" in str(e):
                    pass

    def update_price(self):
        # Updating the price of stocks during market hours
        get_query = "SELECT symbol, curr_price, day_high, day_low, volume FROM stocks"
        output = self.db.run_query(get_query)
        for stock in output:
            updated_price = get_price(stock["curr_price"])
            updated_high, updated_low = stock["day_high"], stock["day_low"]
            volume = stock["volume"]
            if updated_price > stock["day_high"]:
                updated_high = updated_price
            elif updated_price < stock["day_low"]:
                updated_low = updated_price
            update_query = "UPDATE stocks SET prev_curr_price=%s, curr_price=%s, day_low=%s, day_high=%s, " \
                           "mark_cap=%s WHERE symbol=%s "

            self.db.run_query(update_query, stock["curr_price"], float(updated_price), float(updated_low),
                              float(updated_high), float("%.2f" % (updated_price * volume)), stock["symbol"])

    def update_pending_order_table(self):
        clean_orders = []
        # Checking pending orders
        # Deleting triggered orders
        get_query = "SELECT * FROM pending_orders"
        del_query = "DELETE FROM pending_orders WHERE order_id=%s"
        output = self.db.run_query(get_query)
        for order in output:
            expiry_date = order["expiry_date"]
            if order["triggered"]:
                self.db.run_query(del_query, order["order_id"])
                self.db.run_query(
                    "INSERT INTO transaction_his (stock_id,user_id,quantity,price, trans_type, order_type) "
                    "VALUES (%s,%s,%s,%s,%s,%s)",
                    order["stock_id"], order["user_id"], order["quantity"], order["limit_price"], order["trans_type"],
                    order["order_type"])
            elif date.now() > expiry_date and order["triggered"] is False:
                clean_orders.append(order["order_id"])
        # Updating the user funds
        # Deleting expired orders which are not triggered
        for o_id in clean_orders:
            get_query = "SELECT * FROM pending_orders WHERE order_id=%s"
            output = self.db.run_query(get_query, o_id)
            user_data = self.db.run_query('SELECT * FROM user_portfolio WHERE user_id=%s', output["user_id"])
            new_funds = user_data[0]["funds"] + output["price"] * output["quantity"]
            update_fund = "UPDATE user_portfolio SET funds=%s WHERE user_id=%s"
            self.db.run_query(update_fund, new_funds, output["user_id"])
            self.db.run_query(del_query, o_id)
        print("Cleaned pending orders")

    def trigger_pending_orders(self):
        get_query = "SELECT * FROM pending_orders"
        stock_data = "SELECT * FROM stocks WHERE id=%s"
        for p_d in self.db.run_query(get_query):
            output = self.db.run_query(stock_data, p_d["stock_id"])
            if output[0]["curr_price"] >= p_d["limit_price"] and not p_d["triggered"]:
                self.db.run_query("UPDATE pending_orders SET triggered=True WHERE order_id=%s", p_d["order_id"])

    def update_market_open_price(self):
        update_query = "UPDATE stocks SET open_price=%s WHERE id=%s"
        stocks_data = "SELECT * FROM stocks"
        for stock in self.db.run(stocks_data):
            self.db.run_query(update_query, stock["curr_price"], stock["id"])

    def update_market_close_price(self):
        update_query = "UPDATE stocks SET close_price=%s WHERE id=%s"
        stocks_data = "SELECT * FROM stocks"
        for stock in self.db.run(stocks_data):
            self.db.run_query(update_query, stock["curr_price"], stock["id"])
