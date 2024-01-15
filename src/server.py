import string, random
import mysql.connector # MySQL database connection module
import socket, errno
from datetime import datetime, timedelta
import json
import threading
import secrets

class DataHandler():
    def __init__(self):
        self.db = mysql.connector.connect(
        host="127.0.0.1",
        user="mikkeladmin",
        passwd="mikkeladmin",
        database="tempsensorweb"
        )
        self.mycursor = self.db.cursor()

        self.web = WebsiteCommunication(self.db, self.mycursor)


    # Strips HTTP content for JSON payload
    def http_strip(self, recv_rawdata = ""):
        print("[+] Stripping HTTP request for JSON payload...")
        json_start = recv_rawdata.find(b'{')
        json_end = recv_rawdata.find(b'}') + 1
        json_payload = recv_rawdata[json_start:json_end] if json_start != -1 and json_end != 0 else b""

        return json_payload

    # Generate random device id
    def device_generation(self):
        success = 0

        while 0 == success:
            # String generation
            letters = string.ascii_letters + string.digits
            pw = ''.join(random.choice(letters) for i in range(8))
            rtal = ''.join(random.choice(string.digits) for _ in range(5))
            device_id = ('Device#' + rtal)

            # Tjek MySQL db
            self.mycursor.execute('SELECT * FROM device_id WHERE deviceId = %s', (device_id,))
            result = self.mycursor.fetchone()

            if result is None:
                # Input generated string i MySQL db
                try:
                    self.mycursor.execute('INSERT INTO device_id (deviceId, passwd) VALUES (%s,%s)', (device_id, pw))
                    self.db.commit()

                    print('[+] Device ID & Password successfully generated: %s, %s \n' % (device_id, pw))
                    success = 1
                    return device_id
                except Exception as e:
                    print('[!] Encountered exception error while generating device ID: %s' % e)
            else:
                print('[!] Device ID: %s already exist in the database, retrying...' % device_id)

    # Handler af målingsdata fra vandspildsmåleren
    def recordingdata_handler(self, device_id="NULL", temp_pipe=0, temp_room=0):
        try:
            self.mycursor.execute('INSERT INTO tempreadings (device_id, temp_pipe, temp_room) VALUES (%s,%s,%s)', (device_id, temp_pipe, temp_room))
            self.db.commit()

            print('[+] Successfully added Temperature entry for %s \n' % device_id)
        except Exception as e:
            print('[!] Encountered exception error while adding temperature entry: %s' % e)

    # Login request handler
    def login_procedure(self, username, password):
        device_id = ('Device#' + username)
        self.mycursor.execute('SELECT * FROM device_id WHERE deviceId = %s and passwd = %s', (device_id, password))
        result = self.mycursor.fetchone()

        if result:
            print(f"[i] Login Successful for {device_id}. Generating session token...")
            self.web.generate_session(device_id)
        else:
            print(f"[i] Login Failed for {device_id}.")

class WebsiteCommunication:
    def __init__(self, database, cursor):
        self.db = database
        self.mycursor = cursor
        
        self.time_now = datetime.now().strftime("%H%M%S") + timedelta(hours=1) # UTC+1 offset

    def generate_session(self, device_id):
        self.session_id = secrets.token_hex(16)
        self.user_id = secrets.choice(range(10000, 99999))
        
        print(f"Session ID - {self.session_id}, User ID - {self.user_id}, Device ID - {device_id}, Time - {self.time_now}")

        self.mycursor.execute('INSERT INTO session (session_id, user_id, device_id, last_activity) VALUES (%s,%s,%s,%s)', (self.session_id, self.user_id, device_id, self.time_now))
        self.db.commit()

    def cleanup_sessions(self):
        return


class SocketCommunication:
    def __init__(self) -> None:
        HOST: str = '0.0.0.0' # Listen på alle IP'er assigned til serverens interfaces
        PORT_TCP: int = 13371
        PORT_UDP: int = 31337
        backlog = 5

        self.handler = DataHandler()

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

    def handle_tcp_client(self, client_socket, client_addr="?.?.?.?"):
        raw_data = client_socket.recv(1024)
        print(raw_data)
        if b'POST' in raw_data:
            print(f"[+] HTTP POST request recieved from reverse proxy on {client_addr}")
            raw_data = self.handler.http_strip(raw_data)

        client_data_tcp = raw_data.decode('utf-8')

        data_dict_tcp = json.loads(client_data_tcp)
        message_type = data_dict_tcp.get('data', '')

        print(f"[+] Received packet of type '{message_type}' from {client_addr}")

        # Call device ID generation
        if 'device ID request' == message_type:
            device_id = self.handler.device_generation()
            response_data = {'device_id': device_id}
            client_socket.send(json.dumps(response_data).encode('utf-8'))
            print("[i] Device ID successfully sent to ESP \n")        
        elif 'login request' == message_type:
            recv_device_id = data_dict_tcp.get('user', '')
            recv_password = data_dict_tcp.get('pass', '')
            self.handler.login_procedure(recv_device_id, recv_password)
        else:
            print("[!] Error: Unrecognized message type.")
        
    def handle_udp_data(self, udp_data, udp_client_addr):
        data_dict_udp = json.loads(udp_data.decode('utf-8'))
        message_type = data_dict_udp.get('data', '')

        print(f"[+] Received UDP packet of type '{message_type}' from {udp_client_addr}")

        if 'recording data' == message_type:
            print(f"[i] Received {message_type} from {udp_client_addr}, processing...")
            device_id = data_dict_udp.get('device_id', '')
            temp_pipe = data_dict_udp.get('temp_pipe', '')
            temp_room = data_dict_udp.get('temp_room', '')
            print(f"[+] Gathered variables from {udp_client_addr}'s {message_type} packet: {device_id}, {temp_pipe}, {temp_room} \n")

            self.handler.recordingdata_handler(device_id=device_id, temp_pipe=temp_pipe, temp_room=temp_room)
        else:
            return

    def close(self):
        self.srv_socket_tcp.close()
        self.srv_socket_udp.close()

if __name__ == "__main__":
    comsocket = SocketCommunication()
    comsocket.start_listening()