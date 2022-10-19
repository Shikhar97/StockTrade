from stocksymbol import StockSymbol

from lib.db import DB


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
