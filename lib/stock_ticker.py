import random

from stocksymbol import StockSymbol
from lib.db import DB


def get_price(init_value, change_factor=0.007):
    return float("{:.2f}".format(init_value + change_factor * random.randint(int(((init_value + 1) / 2) * -1), int((init_value + 1) / 2))))


class StockList:
    def __init__(self):
        self.api_key = 'ab43c7ee-4009-4e4f-83a4-cf41c59dd486'
        self.ss = StockSymbol(self.api_key)
        self.symbol_list_us = self.ss.get_symbol_list(index="NDX")
        self.db = DB("admin", "admin", "stock_trade")

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
                              float(updated_high), round(updated_price*volume, 2), stock["symbol"])
        print("Updated Stock Prices")