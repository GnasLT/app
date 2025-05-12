import socket
import os
import struct
import time



while True:
    try:
        SERVER_IP = '192.168.1.11'
        PORT = 6666
        RETRY_INTERVAL = 60
        print('Connecting....')
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client_socket.settimeout(5.0)
        client_socket.connect((SERVER_IP, PORT))
        print(f"Connected {SERVER_IP}:{PORT}")
        image_dir = os.path.join(os.path.expanduser('~'), 'Desktop/thesis/images')
                    

        os.makedirs(image_dir, exist_ok=True)

        command = client_socket.recv(1024).decode('utf-8').strip()
        image_path = os.path.join(image_dir, command)
        print(f"Received: {command}")
        os.system(f'rpicam-still -e png -o {image_path}')
        file = open(image_path,'rb')
        data = file.read(1024 * 512)
        while data:
            client_socket.sendall(data)
            data = file.read(1024 * 512)
    except Exception as e:
        print(f"Unexpected error: {e}")
    finally:
        if 'client_socket' in locals():
            client_socket.close()
            time.sleep(RETRY_INTERVAL)

