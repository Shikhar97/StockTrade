import random
from stocksymbol import StockSymbol
from datetime import datetime as date
from apscheduler.schedulers.background import BackgroundScheduler


# To calculate the delta for stock price
def get_price(init_value, change_factor=0.007):
    return float("{:.2f}".format(
        init_value + change_factor * random.randint(int(((init_value + 1) / 2) * -1), int((init_value + 1) / 2))))


class StockList:
    def __init__(self, db_obj):
        self.api_key = 'ab43c7ee-4009-4e4f-83a4-cf41c59dd486'
        # Getting the list of 100 stocks and randomly initialize the values of the stocks
        self.ss = StockSymbol(self.api_key)
        self.symbol_list_us = self.ss.get_symbol_list(index="NDX")
        self.db = db_obj
        # Adding the price update task to run in the background
        self.sched = BackgroundScheduler()
        self.sched.add_job(self.schedule_jobs, 'interval', seconds=59)
        self.sched.start()

    # Wrapper scheduler function for scheduling the background tasks
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
        if d1 > d3:
            if "market_close" in job_list:
                self.sched.remove_job("market_close")
        else:
            if "market_close" not in job_list:
                run_date = date.combine(date.today(), date.time(d3))
                self.sched.add_job(self.update_market_close_price, 'date', run_date=run_date, id="market_close")
            else:
                self.sched.remove_job("market_close")
                run_date = date.combine(date.today(), date.time(d3))
                self.sched.add_job(self.update_market_close_price, 'date', run_date=run_date, id="market_close")


        # Update the open price once market opens
        if d1 > d2:
            if "market_open" in job_list:
                self.sched.remove_job("market_open")
        else:
            if "market_open" not in job_list:
                run_date = date.combine(date.today(), date.time(d2))
                self.sched.add_job(self.update_market_open_price, 'date', run_date=run_date, id="market_open")
            else:
                self.sched.remove_job("market_open")
                run_date = date.combine(date.today(), date.time(d2))
                self.sched.add_job(self.update_market_open_price, 'date', run_date=run_date, id="market_open")

        # Update market prices every 15 seconds
        if d2 <= d1 <= d3:
            if "market_update" not in job_list:
                self.sched.add_job(self.update_price, 'interval', seconds=13, id="market_update")
        else:
            if "market_update" in job_list:
                self.sched.remove_job("market_update")

        # Update pending orders every 31 seconds
        if "update_pending_order" not in job_list:
            self.sched.add_job(self.update_pending_order_table, 'interval', seconds=5, id="update_pending_order")

        # Check and trigger pending orders every 2 seconds
        if "trigger_pending_orders" not in job_list:
            self.sched.add_job(self.trigger_pending_orders, 'interval', seconds=14, id="trigger_pending_orders")
        print(job_list)

    # Initialize db with stocks and their prices
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

    # Function to update the price, day_high, day_low, etc.
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

    # Function to update the pending orders
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
            elif date.now() > date.strptime(expiry_date.strftime("%Y-%m-%d"), "%Y-%m-%d") and \
                    order["triggered"] is False:
                clean_orders.append(order["order_id"])
        # Updating the user funds
        # Deleting expired orders which are not triggered
        for o_id in clean_orders:
            get_query = "SELECT * FROM pending_orders WHERE order_id=%s"
            output = self.db.run_query(get_query, o_id)
            user_data = self.db.run_query('SELECT * FROM user_portfolio WHERE user_id=%s', output[0]["user_id"])
            new_funds = user_data[0]["funds"] + output[0]["limit_price"] * output[0]["quantity"]
            update_fund = "UPDATE user_portfolio SET funds=%s WHERE user_id=%s"
            self.db.run_query(update_fund, new_funds, output[0]["user_id"])
            self.db.run_query(del_query, o_id)
        print("Cleaned pending orders")

    # Function to trigger pending limit order if the price matches the current order
    def trigger_pending_orders(self):
        get_query = "SELECT * FROM pending_orders"
        stock_data = "SELECT * FROM stocks WHERE id=%s"
        for p_d in self.db.run_query(get_query):
            output = self.db.run_query(stock_data, p_d["stock_id"])
            if p_d["trans_type"].lower() == "sell":
                if output[0]["curr_price"] >= p_d["limit_price"] and not p_d["triggered"]:
                    self.db.run_query("UPDATE pending_orders SET triggered=True WHERE order_id=%s", p_d["order_id"])
            elif p_d["trans_type"].lower() == "buy":
                if output[0]["curr_price"] <= p_d["limit_price"] and not p_d["triggered"]:
                    self.db.run_query("UPDATE pending_orders SET triggered=True WHERE order_id=%s", p_d["order_id"])
        print("Triggered pending orders")

    # To update the open price for each stock, executes once the market opens
    def update_market_open_price(self):
        update_query = "UPDATE stocks SET open_price=%s WHERE id=%s"
        stocks_data = "SELECT * FROM stocks"
        for stock in self.db.run_query(stocks_data):
            self.db.run_query(update_query, stock["curr_price"], stock["id"])
        print("Update Open price")

    # To update the close price for each stock, executes once the market closes
    def update_market_close_price(self):
        update_query = "UPDATE stocks SET close_price=%s WHERE id=%s"
        stocks_data = "SELECT * FROM stocks"
        for stock in self.db.run_query(stocks_data):
            self.db.run_query(update_query, stock["curr_price"], stock["id"])
        print("Updated Close price")
