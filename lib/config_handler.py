from lib.db import DB


class Config:
    def __init__(self):
        self.db_name = "stock_trade"
        self.db_user = "admin"
        self.db_password = "admin"
        self.db_obj = DB(self.db_user, self.db_password, self.db_name)


__builtins__["config"] = Config()
