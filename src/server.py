import string, random
import mysql.connector # MySQL database connection module
import socket
import errno
import time
import json

db = mysql.connector.connect(
    host="127.0.0.1",
    user="mikkeladmin",
    passwd="mikkeladmin",
    database="tempsensorweb"
)
mycursor = db.cursor()

# Generate random device id, 
def id_gen():

    success = 0

    while 0 == success:
        # String generation
        letters = string.ascii_letters + string.digits
        pw = ''.join(random.choice(letters) for i in range(8))
        rtal = ''.join(random.choice(string.digits) for _ in range(5))
        device_id = ('Device#' + rtal)
        print(f'device_id: {device_id} \npasswd: {pw}')

        # Tjek MySQL db
        mycursor.execute('SELECT * FROM device_id WHERE deviceId = %s', (device_id,))
        result = mycursor.fetchone()

        if result is None:
            # Input generated string i MySQL db
            try:
                mycursor.execute('INSERT INTO device_id (deviceId, passwd) VALUES (%s,%s)', (device_id, pw))
                db.commit()

                print('[+] Device ID successfully generated: %s' % device_id)
                success = 1
                return device_id
            except Exception as e:
                print('[!] Encountered exception error: %s' % e)
        else:
            print('[!] Device ID already exist in the database, retrying...')

# Modtager af målingsdata fra vandspildsmåleren
def rdata_recv(device_id = "Error", temp_pipe = "Error", temp_room = "Error"):
    return

class NetworkCom:
    def __init__(self) -> None:
        HOST: str = '0.0.0.0' # Listen på alle IP'er assigned til serverens interfaces
        PORT: int = 13371
        backlog = 5

        self.srv_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        
        try:
            self.srv_socket.bind((HOST, PORT))
            print('[i] Waiting for connection...')
        except OSError as e:
            if e.errno == errno.EADDRINUSE:
                print('[!] Address Already in use, rebinding...')
                self.srv_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
                self.srv_socket.bind((HOST, PORT))
                print('[i] Rebinding succeded.')
            else:
                print('[!] Socket error: %s' % e)
        self.srv_socket.listen(backlog)

    def accept_connection(self):
        client_socket, client_addr = self.srv_socket.accept()

        try:
            self.handle_client(client_socket)
        except Exception as e:
            print('Error handeling client: %s' % e)
        finally:
            client_socket.close()

    def handle_client(self, client_socket):
        client_data = client_socket.recv(1024).decode('utf-8')
        print(client_data)

        try:
            # Assuming the data is a JSON string
            data_dict = json.loads(client_data)
            message_type = data_dict.get('data', '')

            if message_type == 'device ID request':
                device_id = id_gen()
                client_socket.send(device_id.encode('utf-8'))

            elif message_type == 'recording data':
                temp_pipe = data_dict.get('temp_pipe', '')
                temp_room = data_dict.get('temp_room', '')
                
                print(temp_pipe, temp_room)

            else:
                pass

        except json.JSONDecodeError as e:
            print(f"Error decoding JSON: {e}")

        client_socket.close()

    def close(self):
        self.srv_socket.close()

if __name__ == "__main__":
     socket = NetworkCom()
     while True:
         socket.accept_connection()