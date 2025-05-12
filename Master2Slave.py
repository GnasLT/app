import socket
import os

class Master2Slave:
    def __init__(self,ip,port,time):
        self.ip = ip
        self.port = port
        self.name = f'rgb_{time}.png'
        self.connection,self.client_address = self.connect()
    def connect(self):
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_socket:
                server_socket.bind((self.ip,self.port))
                server_socket.listen(1)
                print(f'Server is listening {self.ip}:{self.port}....')
                
                connection, client_address = server_socket.accept()
                return connection, client_address
        except Exception as e:
            print(f"Error getting image from slave: {e}")
            return None, None
    
    def sendcommand(self):
        self.connection.sendall(self.name.encode('utf-8'))
        
    def getimage(self):
        save_dir = os.path.join(os.path.expanduser('~'), 'Desktop/thesis/images')
        os.makedirs(save_dir, exist_ok=True)
        
        
        try:
                with open(os.path.join(save_dir, self.name) ,'wb') as file:
                    while True:
                        chunk = self.connection.recv(1024 * 1024)  
                        if not chunk:  
                            break
                        file.write(chunk)
                
               
                print(f"Saved at: {os.path.join(save_dir, self.name)}")
                return os.path.join(save_dir, self.name)
            
        except Exception as e:
                print(f"error: {e}")
                if os.path.exists(os.path.join(save_dir, self.name)):
                    os.remove(os.path.join(save_dir, self.name))  
                return None
                """
        with open(os.path.join(save_dir, self.name), 'wb') as file:
            while True:
                chunk = self.connection.recv(1024 * 1024)  # 1MB chunks
                if not chunk:
                    break
                file.write(chunk)
        
        print('Received image')
        return os.path.join(save_dir, self.name)"""
