from pymongo import MongoClient
import urllib.parse
import DBconnect




class Plant:
    def __init__(self, plantid ='', plantname = ''):
        self.name = plantname
        self.id = plantid
        self.client = None
        self.collection = self.get_collection()
    def get_collection(self):
        self.client = DBconnect.DBconnect()
        db = self.client.getdb()
        return db['Plant']
    def savedata(self):
        data = {
            '_id': self.id,
            'name': self.name
            }
        self.collection.insert_one(data)
    def close_connetion(self):
        self.client.close()
    def check_plant_exist(self,plantid):
        check = self.findbyid(plantid)
        if check != None:
            return check
        return None
    def deleteone(self,_id = ''):
        self.collection.delete_one({'_id': _id})
        return True
    
    def updateone(self,query = '',update= ''):
        self.collection.update_one(query,{"$set" : update})
        return True
    
    def insertone(self,_id = '',name = ''):
        self.collection.insert_one({'_id': _id, 'name': name})
        return True
        
    def findone(self,query = None):
        if querry != None:
            return self.collection.find_one(querry)
        
        return self.collection.find_one().sort("timestamp", -1)
        
    def findmany(self, query = None):
        if query != None:
            return self.colletion.find(query)
        return list(self.collection.find(query).sort("timestamp", -1))

    def findbyid(self, _id = ''):
        result = self.collection.find_one({'_id': _id})
        return result
    
    def findbyname(self, plant_name):
        return self.collection.find_many({'name': plant_name})
    
    def __del__(self):
        self.close_connetion()