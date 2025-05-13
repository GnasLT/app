from pymongo import MongoClient
import urllib
user_name= 'gnas'
pass_word = 'gnas'
host = 'localhost'
port =27017
client = MongoClient(f'mongodb://{user_name}:{urllib.parse.quote_plus(pass_word)}@{host}:{port}')
db = client['plant_data']
def create_collection(name, validator):
    db.command('collMod', name, validator)
# colletion Plant
db.create_collection('Plant')
plant_validator = {
        '$jsonSchema': {
            'bsonType': 'object',
            'required': ['name'],
            'properties': {
                'name': {'bsonType': 'string'}
            }
        }
    }
create_collection('Plant',plant_validator)
# colletion SensorData
db.create_collection('SensorData')
sensor_validator = {
        '$jsonSchema': {
            'bsonType': 'object',
            'required': ['plant_id','time', 'value', 'unit'],
            'properties': {
                'plant_id': {'bsonType': 'objectId'},
                'time': {'bsonType': 'timestamp'},
                'values': {
                    'bsonType': 'array',
                    'minItems': 1,
                     'items': {
                        'bsonType': 'object',
                        'required': ['type', 'value'],
                        'properties': {
                            'type': {
                                'bsonType': 'string',
                                'enum': ['temperature', 'humidity', 'light', 'co2', 'moisture'],
                                },
                            'value':{
                                'bsonType': ['double', 'int', 'decimal'],
                                },
                            'unit': {
                                'bsonType': 'string',
                                }
                    }
                }
            }
        }
    }
}

#collection = db['SensorData']
#collection.drop()
create_collection('SensorData',sensor_validator)

# colletion ImageData
db.create_collection('ImageData')
image_validator = {
    '$jsonSchema': {
        'bsonType': 'object',
        'required': ['plant_id','images', 'time'],
        'properties': {
            'plant_id': {'bsonType': 'objectId'},
                'images':{
                    'bsonType': 'array',
                    'minItems': 1,
                    'items': {
                        'bsonType': 'object',
                        'required': ['type', 'path'],
                        'properties': {
                            'type': {
                            'bsonType': 'string',
                            'enum': ['rgb','nir'],
                                },
                            'path':{
                                'bsonType': 'string',
                                },
                            'resolution': {
                                    'bsonType': 'string'
                                    }
                    },
                    'time': {'bsonType': 'timestamp'}
                }
            }
        }
   }
}

create_collection('ImageData',image_validator)
# colletion PlantIndex
db.create_collection('PlantIndex')
plant_index_validator = {
            '$jsonSchema': {
                'bsonType': 'object',
                'required': ['plant_id', 'time', 'NDVI', 'rgb_id', 'nir_id', 'image_path'],
                'properties': {
                    #'plant_id': {'bsonType': 'objectId'},
                    'time': {'bsonType': 'timestamp'},
                    'NDVI': {'bsonType': 'array'},
                    #maybe more index
                    'image2analysis': {'bsonType': 'objectId'},
                    #'image_path': {'bsonType': 'string'}
                }
            }
        }

create_collection('PlantIndex',plant_index_validator)
collection = db['Plant']
data = {
    '_id': 'plant1',
    'name': 'Rau tan day la'
    }
collection.insert_one(data)
print('Success')
