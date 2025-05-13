import board
import datetime
import adafruit_bh1750 as bh1750
import adafruit_am2320
import mh_z19
import time
import asyncio
import streamlit as st
import DBconnect
from queue import Queue
import ImageData

class SensorData:
    def __init__(self, plant_id='',time = 15):
        self.plant_id = plant_id
        self.is_running = False
        self.i2c = board.I2C()
        self.collection = self.get_collection()
        self.timeout = 60*time
        self.data_queue = Queue()
        
    def start(self):
        
        self.is_running = True
        self.run()
    def get_collection(self):
        self.client = DBconnect.DBconnect()
        db = self.client.getdb()
        return db['SensorData']
       
    def read_co2(self):
        try:
           
            data = mh_z19.read_from_pwm()
            #return data.get('co2')
            self.co2 = data.get('co2')
        except Exception as e:
            print(f"CO2 sensor error: {e}")

    def read_light(self):
        try:
            
            data = bh1750.BH1750(self.i2c)
            self.light = data.lux
        except Exception as e:
            print(f"Light sensor error: {e}")

    def read_air(self):
        try:
            
            data = adafruit_am2320.AM2320(self.i2c)
            self.temperature = data.temperature
            self.humidity = data.relative_humidity
        except Exception as e:
            print(f"Air sensor error: {e}")

    def save_sensor_data(self, time):
        if not self.collection:
            print("No database connection available")
            return False
        try:
            data = {
                'plant_id': self.plant_id,
                'time': time,
                'values': [
                    {'type': 'light', 'value': self.light, 'unit': 'lux'},
                    {'type': 'temperature', 'value': self.temperature, 'unit': '*C'},
                    {'type': 'humidity', 'value': self.humidity, 'unit': '%RH'},
                    {'type': 'co2', 'value': self.co2, 'unit': 'ppm'}
                ]
            }
            self.collection.insert_one(data)
            
            return True
        except Exception as e:
            print(f"Failed to save sensor data: {e}")
            return False
    def readsensor(self):
        self.read_co2()
        self.read_air()
        self.read_light()
        
    def run(self):
       
        while self.is_running:
            
            self.readsensor()
            self.timegetdata = datetime.datetime.now().strftime("%d-%m-%Y_%H:%M")
            self.data_queue.put({
                #'Plant ID': self.plant_id,
                'Time': self.timegetdata,
                'Light (lux)' : self.light,
                'Temperature (*C)' : self.temperature,
                'Humidity (%RH)' : self.humidity,
                'CO2 (ppm)' : self.co2
            })
            self.save_sensor_data(self.timegetdata)
            
            imgdata = ImageData.ImageData(self.plant_id)
            imgdata.capture_and_save_image_data()
            time.sleep(self.timeout)
        
    def stop(self):
        self.is_running = False
        self.close_connection()
        
    def close_connection(self):
        self.client.close()
        
    def insertone(self,query = None):
        if query != None:
            self.collection.insert_one(query)

    def findmany(self, query = None):
        if query != None:
            return self.collection.find(query)
        return list(self.collection.find(query).sort("timestamp", -1))
        
    def aggregate(self, pipe = None):
        if pipe != None:
            return self.collection.aggregate(pipe)
        return None
        
    def findone(self, query = None):
        if query != None:
            return self.collection.find_one(query)
        return self.collection.find_one(sort= [("timestamp", 1)])
    
    def findbyid(self,query = None):
        if query != None:
            return self.collection.find_one({'_id': query})
        return None
