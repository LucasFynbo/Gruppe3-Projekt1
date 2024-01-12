import string, random
import mysql.connector # MySQL database connection module
import socket, errno
import time
import json
import threading

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

        # Tjek MySQL db
        mycursor.execute('SELECT * FROM device_id WHERE deviceId = %s', (device_id,))
        result = mycursor.fetchone()

        if result is None:
            # Input generated string i MySQL db
            try:
                mycursor.execute('INSERT INTO device_id (deviceId, passwd) VALUES (%s,%s)', (device_id, pw))
                db.commit()

                print('[+] Device ID & Password successfully generated: %s, %s' % (device_id, pw))
                success = 1
                return device_id
            except Exception as e:
                print('[!] Encountered exception error: %s' % e)
        else:
            print('[!] Device ID: %s already exist in the database, retrying...' % device_id)

# Handler af målingsdata fra vandspildsmåleren
def rdata_handler(device_id = "Error", temp_pipe = "Error", temp_room = "Error"):
    return

class NetworkCom:
    def __init__(self) -> None:
        HOST: str = '0.0.0.0' # Listen på alle IP'er assigned til serverens interfaces
        PORT_TCP: int = 13371
        PORT_UDP: int = 31337
        backlog = 5

        self.srv_socket_tcp = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.srv_socket_udp = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        try:
            self.srv_socket_tcp.bind((HOST, PORT_TCP))
            self.srv_socket_udp.bind((HOST, PORT_UDP))
            print('[i] Waiting for connection... \n\n')
        except OSError as e:
            if e.errno == errno.EADDRINUSE:
                print('[!] Address Already in use, rebinding...')
                # TCP socket rebinding
                self.srv_socket_tcp.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
                self.srv_socket_tcp.bind((HOST, PORT_TCP))

                # UDP socket rebinding
                self.srv_socket_udp.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
                self.srv_socket_udp.bind((HOST, PORT_UDP))
                print('[i] Rebinding succeded.')
            else:
                print('[!] Socket error: %s' % e)
        self.srv_socket_tcp.listen(backlog)

    def start_listening(self):
            tcp_thread = threading.Thread(target=self.accept_tcp_connections)
            udp_thread = threading.Thread(target=self.accept_udp_connections)

            tcp_thread.start()
            udp_thread.start()

            tcp_thread.join()
            udp_thread.join()

    def accept_tcp_connections(self):
            while True:
                client_socket_tcp, client_addr = self.srv_socket_tcp.accept()

                try:
                    self.handle_tcp_client(client_socket_tcp, client_addr)
                except Exception as e:
                    print('Error handling TCP client: %s' % e)
                finally:
                    client_socket_tcp.close()

    def accept_udp_connections(self):
        while True:
            udp_data, udp_client_addr = self.srv_socket_udp.recvfrom(1024)
            try:
                self.handle_udp_data(udp_data, udp_client_addr)
            except Exception as e:
                print('Error handling UDP data: %s' % e)

    def handle_tcp_client(self, client_socket, client_addr):
        client_data_tcp = client_socket.recv(1024).decode('utf-8')
        data_dict_tcp = json.loads(client_data_tcp)
        message_type = data_dict_tcp.get('data', '')

        print(f"[+] Received packet with type '{message_type}' from {client_addr}")

        if 'device ID request' == message_type:
            device_id = id_gen()
            response_data = {'device_id': device_id}
            client_socket.send(json.dumps(response_data).encode('utf-8'))
            print("[i] Device ID successfully sent to ESP \n")

    def handle_udp_data(self, udp_data, udp_client_addr):
        data_dict_udp = json.loads(udp_data.decode('utf-8'))
        message_type = data_dict_udp.get('data', '')

        print(f"[+] Received UDP packet with type '{message_type}' from {udp_client_addr}")

        if 'recording data' == message_type:
            print(f"[i] Received {message_type} from {udp_client_addr}, processing...")
            device_id = data_dict_udp.get('device_id', '')
            temp_pipe = data_dict_udp.get('temp_pipe', '')
            temp_room = data_dict_udp.get('temp_room', '')
            print(f"[+] Gathered variables from {udp_client_addr}'s {message_type} packet: {device_id}, {temp_pipe}, {temp_room} \n")

    def close(self):
        self.srv_socket_tcp.close()
        self.srv_socket_udp.close()

if __name__ == "__main__":
    socket = NetworkCom()
    socket.start_listening()