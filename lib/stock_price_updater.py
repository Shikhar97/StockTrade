import random
from lib.db import DB


class UpdateStock:
    def __init__(self):
        self.db = DB("admin", "admin", "stock_trade")

    def get_price(self, init_value, change_factor=0.8):
        return float("{:.2f}".format(init_value + change_factor * random.randint(int(((init_value + 1) / 2) * -1),
                                                                                 int((init_value + 1) / 2))))

    def update_price(self):
        # Updating the price of stocks and updating the DB
        get_query = "SELECT symbol, curr_price FROM stocks"
        output = self.db.run_query(get_query)
        for stock_symbol, stock_price in output:
            print(self.get_price(stock_price))
            update_query = "UPDATE stocks SET curr_price='%s' WHERE symbol=%s"
            self.db.run_query(update_query, self.get_price(stock_price), stock_symbol)
            print(self.db.cursor.statusmessage)
        print("Updated Stock Prices")
