import random

from lib.db import DB


class UpdateStock:
    def __init__(self):
        self.db = DB("admin", "admin", "stock_trade")

    def get_price(self, init_value, change_factor=0.8):
        return float("{:.2f}".format(init_value + change_factor * random.randint(-init_value/2, init_value/2)))

    def update_price(self,):
        # Updating the price of stocks and updating the DB
        get_query = "SELECT symbol, curr_price FROM stocks"
        output = self.db.run_query(get_query)
        for stock_name, stock_price in output:
            update_query = "UPDATE stocks SET stock_price=%s WHERE stock_name=%s"
            self.db.run_query(update_query,(self.get_price(stock_price), stock_name))
            if "UPDATE 0 1" not in self.db.cursor.statusmessage:
                print("not working")



# print(get_price(100))