import DBconnect
import socket
import Master2Slave
import datetime
import os


class ImageData:
    def __init__(self, plant_id='plant1'):
        self.plant_id = plant_id
        self.collection = self.getcollection()
    def getcollection(self):
        self.client = DBconnect.DBconnect()
        db = self.client.getdb()
        return db['ImageData']
    
    def close(self):
        self.client.close()
        
    def save_image_data(self, rgb_path, nir_path, time):
        try:
            data = {
                'plant_id': self.plant_id,
                'time': time,
                'values': [
                    {'type': 'rgb', 'path': rgb_path, 'resolution': '2592x1944px'},
                    {'type': 'nir', 'path': nir_path, 'resolution': '3280x2464px'}
                ]
            }
            self.collection.insert_one(data)
            return True
        except Exception as e:
            print(f"Failed to save image data: {e}")
            return False
    
    """def get_image_from_slave(self, time):
        image_name = f'rgb_{time}.png'
        ip = '192.168.1.23'
        port = 6666
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_socket:
                server_socket.bind((ip, port))
                server_socket.listen(1)
                print(f'Server is listening {ip}:{port}....')
                
                connection, client_address = server_socket.accept()
                print(f'Connected to {client_address}')
                
                connection.sendall(image_name.encode('utf-8'))
                print('Command sent')
                
                save_dir = os.path.join(os.path.expanduser('~'), 'Desktop/thesis/images')
                os.makedirs(save_dir, exist_ok=True)
                
                with open(os.path.join(save_dir, image_name), 'wb') as file:
                    while True:
                        chunk = connection.recv(1024 * 1024)  # 1MB chunks
                        if not chunk:
                            break
                        file.write(chunk)
                
                print('Received image')
                return os.path.join(save_dir, image_name)
                
        except Exception as e:
            print(f"Error getting image from slave: {e}")
            return None"""
    def get_image_from_slave(self,time):
        hostname = socket.gethostname()
        ip = socket.gethostbyname(hostname)
        slave = Master2Slave.Master2Slave('192.168.1.11',6666,time)
        slave.sendcommand()
        return slave.getimage()
    def capture_nir_image(self, time):
        image_name = f'nir_{time}.png'
        image_dir = os.path.join(os.path.expanduser('~'), 'Desktop/thesis/images')
        os.makedirs(image_dir, exist_ok=True)
        image_path = os.path.join(image_dir, image_name)
        try:
            os.system(f'rpicam-still -e png -o {image_path}')
            return image_path
        except Exception as e:
            print(f"Error capturing NIR image: {e}")
            return None

    def capture_and_save_image_data(self):
        current_time = datetime.datetime.now()
        formatted_time = current_time.strftime("%d-%m-%Y_%H:%M")
        # Image data
        rgb_path = self.get_image_from_slave(formatted_time)
        nir_path = self.capture_nir_image(formatted_time)
        
        if rgb_path and nir_path:
            self.save_image_data(
                rgb_path,
                nir_path,
                formatted_time
            )
        print('success________________________________________________________')
    def find_one(self,query = None):
        if query != None:
            return self.collection.find_one(query)
        return self.collection.find_one(query)
    
    def find_many(self, query = None):
        if query != None:
            return self.collection.find(query)
        return list(self.collection.find(query).sort("timestamp", -1))
    
    def find_time(self, query = None):
        if query != None:
            return self.collection.aggregate(query)
        return None
        
    
