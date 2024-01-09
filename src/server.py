import string, random
import mysql.connector # MySQL database connection module
import socket
import errno
import time

db = mysql.connector.connect(
    host="79.171.148.173",
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
            kode = ''.join(random.choice(letters) for i in range(8))
            rtal = ''.join(random.choice(string.digits) for _ in range(5))
            device_id = ('Device#' + rtal)
            print(device_id)
            pw = kode
            print(kode)

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
        request = client_socket.recv(1024).decode('utf8')

        if 'request device ID' in request:
            device_id: str = id_gen()

            client_socket.send(device_id.encode('utf-8'))

        client_socket.close()

    def close(self):
        self.srv_socket.close()

if __name__ == "__main__":
     socket = NetworkCom()
     while True:
         socket.accept_connection()