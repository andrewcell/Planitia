from pymongo import MongoClient, errors
import configuration
import datetime

class MongoDB:
    def __init__(self):
        try:
            self.client = MongoClient(configuration.config["mongodb"])
            self.database = self.client[configuration.config["mongodb_db"]]
        except:
            pass

    def Account(self):
        return self.database.accounts

    def findAccount(self, username, password):
        account = self.Account()
        return account.find_one({"identify": username, "password": password})

    def newAccount(self, username, password, firstname, lastname, email, ip, useragent):
        account = self.Account()
        newAccount = {
            "identify": username,
            "password": password,
            "firstname": firstname,
            "lastname": lastname,
            "email": email,
            "admin": False,
            "registerinfo": {
                "useragent": useragent,
                "ip": ip
            },
            "verified": {
                "admin": True,
                "email": True,
                "phone": True
            },
            "phone": {
                "countrycode": "1",
                "number": "1111111111"
            },
            "created_at": datetime.datetime.now(),
            "last_login": None
        }
        try:
            return account.insert_one(newAccount).inserted_id
        except errors.DuplicateKeyError:
            pass