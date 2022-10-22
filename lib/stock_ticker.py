import datetime
import random

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
        # Updating the price of stocks and updating the DB
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
            update_query = "UPDATE stocks SET curr_price=%s, day_low=%s, day_high=%s, mark_cap=%s WHERE symbol=%s"
            self.db.run_query(update_query, float(updated_price), float(updated_low),
                              float(updated_high), float("%.2f" % (updated_price * volume)), stock["symbol"])
        print("Updated Stock Prices")

    def update_pending_orders(self):
        clean_orders = []
        # Checking pending orders and updating them
        get_query = "SELECT * FROM pending_orders"
        output = self.db.run_query(get_query)
        for order in output:
            expiry_date = order["expiry_date"]
            if datetime.datetime.now() > expiry_date and order["triggered"] is False:
                clean_orders.append(order["order_id"])

        del_query = "DELETE FROM pending_orders WHERE order_id=%s"

        # Updating the user funds
        for o_id in clean_orders:
            get_query = "SELECT * FROM pending_orders WHERE order_id=%s"
            output = self.db.run_query(get_query, o_id)
            user_data = self.db.run_query('SELECT * FROM user_portfolio WHERE user_id=%s', output["user_id"])
            new_funds = user_data[0]["funds"] + output["price"] * output["quantity"]
            update_fund = "UPDATE user_portfolio SET funds=%s WHERE user_id=%s"
            self.db.run_query(update_fund, new_funds, output["user_id"])
            self.db.run_query(del_query, o_id)
        print("Cleaned pending orders")

    def remove_triggered_orders(self):
        # Checking pending orders and updating them
        get_query = "SELECT * FROM pending_orders"
        del_query = "DELETE FROM pending_orders WHERE order_id=%s"
        output = self.db.run_query(get_query)
        for order in output:
            if order["triggered"]:
                self.db.run_query(del_query, order["order_id"])
                self.db.run_query(
                    "INSERT INTO transaction_his (stock_id,user_id,quantity,price, trans_type, order_type) "
                    "VALUES (%s,%s,%s,%s,%s,%s)",
                    order["stock_id"], order["user_id"], order["quantity"], order["limit_price"], order["trans_type"],
                    order["order_type"])