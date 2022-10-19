import random

from stocksymbol import StockSymbol
from lib.db import DB


def get_price(init_value, change_factor=0.8):
    return float("{:.2f}".format(init_value + change_factor * random.randint(int(((init_value + 1) / 2) * -1),
                                                                             int((init_value + 1) / 2))))


class StockList:
    def __init__(self):
        self.api_key = 'ab43c7ee-4009-4e4f-83a4-cf41c59dd486'
        self.ss = StockSymbol(self.api_key)
        self.symbol_list_us = self.ss.get_symbol_list(index="NDX")
        self.db = DB("admin", "admin", "stock_trade")

    def initialize_db(self):
        for stock in self.symbol_list_us:
            try:
                self.db.run_query("INSERT INTO stocks (symbol, stock_name) VALUES (%s, %s)", stock["symbol"], stock["longName"])
                if "INSERT 0 1" not in self.db.cursor.statusmessage:
                    print("Cannot insert")
            except Exception as e:
                if "already exists" in str(e):
                    pass

    def update_price(self):
        # Updating the price of stocks and updating the DB
        get_query = "SELECT symbol, curr_price FROM stocks"
        output = self.db.run_query(get_query)
        for stock_symbol, stock_price in output:
            update_query = "UPDATE stocks SET curr_price='%s' WHERE symbol=%s"
            self.db.run_query(update_query, get_price(stock_price), stock_symbol)
        print("Updated Stock Prices")
