import urllib.parse
from pymongo import MongoClient


class DBconnect:
    def __init__(self,username= 'gnas', password ='gnas',host = 'localhost',port = 27017):
        self.username = username
        self.password = password
        self.host = host
        self.port = port
        self.mongo_client = self.connect()
    def connect(self):
        try:
            mongo_client = MongoClient(
                f'mongodb://{self.username}:{urllib.parse.quote_plus(self.password)}@{self.host}:{self.port}'
            )
            mongo_client.server_info()
            return mongo_client
        except Exception as e:
            print(f"Database connection failed: {e}")
            return None
        
    def getdb(self):
        return self.mongo_client['plant_data']
    def close(self):
        if self.mongo_client:
            self.mongo_client.close()
        