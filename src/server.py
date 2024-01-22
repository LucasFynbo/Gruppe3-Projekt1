import bcrypt
import mysql.connector # MySQL database connection module
import socket, errno
from datetime import datetime, timedelta
import json
import threading
import secrets
import time

class DataHandler():
    def __init__(self):
        self.db = mysql.connector.connect(
        host="127.0.0.1",
        user="mikkeladmin",
        passwd="mikkeladmin",
        database="tempsensorweb"
        )
        self.mycursor = self.db.cursor()

        self.session = SessionHandler(self.db, self.mycursor)

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
            pw = secrets.token_urlsafe(8)
            hashPass = bcrypt.hashpw(pw.encode('utf-8'), bcrypt.gensalt())
            rtal = secrets.choice(range(10000, 99999))
            device_id = ('Device#' + str(rtal))

            # Tjek MySQL db
            self.mycursor.execute('SELECT * FROM device_id WHERE deviceId = %s', (device_id,))
            result = self.mycursor.fetchone()

            if result is None:
                # Input generated string i MySQL 
                try:
                    self.mycursor.execute('INSERT INTO device_id (deviceId, passwd) VALUES (%s,%s)', (device_id, hashPass))
                    self.db.commit()

                    # Create user configuration for det nye device ID
                    default_name = device_id
                    renamed_id_value = f"{device_id}={default_name}"
                    self.mycursor.execute('INSERT INTO userConfiguration (source_device_ID, linked_device_ID, renamed_ID) VALUES (%s,%s,%s)', (device_id, ','+device_id, renamed_id_value))
                    self.db.commit()

                    print('[+] Device ID & Password successfully generated: %s, %s \n' % (device_id, pw))
                    success = 1
                    return device_id, pw
                except Exception as e:
                    print('[!] Encountered exception error while generating device ID: %s' % e)
            else:
                print('[!] Device ID: %s already exist in the database, retrying...' % device_id)
        
    #Udregning af gennemsnits temperatur,tager fra de sidste 24 timer           
    def alarm(self, src_device_id):
        try: 
            self.mycursor.execute('SELECT temp_pipe, temp_room FROM tempreadings WHERE device_id = %s', (src_device_id,))
            readings = self.mycursor.fetchall()

        #Udregn selve gennemsnitstemperaturen
            if len(readings) > 1:
                tempDifs = [readings[i][0] - readings [i][1] for i in range (1, len (readings))]
                avgDif = sum (tempDifs) / len (tempDifs)
            print(f'[i] Average Temperature Difference: {avgDif}')
        
            alarmThreshold = 3 #Tolerancen for temperatur forskel

            if avgDif > alarmThreshold: #hvis gennemsnitsforskellen er større end tolerancen
                print (f"[!] Alarm Triggered! Average temperature exceeds threshold: {avgDif}")
            

        except Exception as e:
            print ('[!] Error in calculating average temperature difference: %s' % e)
            return None

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

        login_status = self.session.authenticate(device_id, password)

        if 'AuthSucceed' == login_status:
            SessionToken, UserId = self.session.GenerateSessionToken(device_id)
            print (f"[+] Session Token for {device_id}: {SessionToken}")

            self.session.storeSessionToken(device_id, SessionToken, UserId)
 
            set_cookie_header = f"Set-Cookie: session_id={SessionToken}; username={device_id}; Secure; HttpOnly\r\n"
            response_data = {
            'status': 'Login: Credentials accepted'
            }
            response_body = json.dumps(response_data)

            response = "HTTP/1.1 200 OK\r\n"
            response += set_cookie_header
            response += f"Content-Type: application/json\r\n"
            response += f"Content-Length: {len(response_body)}\r\n"
            response += "\r\n"
            response += response_body
            return response

        elif 'AuthFailed':
            response_data = {
            'status': 'Error: Invalid credentials'
            }
            response_body = json.dumps(response_data)

            response = "HTTP/1.1 401 Unauthorized\r\n"
            response += f"Content-Type: application/json\r\n"
            response += f"Content-Length: {len(response_body)}\r\n"
            response += "\r\n"
            response += response_body
            return response
        else:
            response_data = {
            'status': 'Error: Unknown Error'
            }
            response_body = json.dumps(response_data)

            response = "HTTP/1.1 520 Unknown Error\r\n"
            response += f"Content-Type: application/json\r\n"
            response += f"Content-Length: {len(response_body)}\r\n"
            response += "\r\n"
            response += response_body
            return response

    def sessionCookieAuthHandler(self, recv_rawdata):
        cookieStatus, src_device_id = self.session.sessionCookieAuth(recv_rawdata)
        
        if 'AuthSucceed' == cookieStatus:
            linked_devices = self.getLinkedDevices(src_device_id)
            linked_device_names = self.getLinkedDeviceNames(linked_devices)

            print(f"\n\nTest printing functions: getLinkedDevices: {linked_devices}, \ngetLinkedDeviceNames: {linked_device_names}\n\n")

            response_data = {
            'status': 'Session: Authorization confirmed',

            'linked_devices': f'{linked_devices}',
            'linked_device_names': f'{linked_device_names}'
            }
            response_body = json.dumps(response_data)

            response = "HTTP/1.1 200 OK\r\n"
            response += f"Content-Type: application/json\r\n"
            response += f"Content-Length: {len(response_body)}\r\n"
            response += "\r\n"
            response += response_body
            return response
        
        elif 'AuthFailed' == cookieStatus:
            response_data = {
            'status': 'Error: Session Time-out'
            }
            response_body = json.dumps(response_data)

            response = "HTTP/1.1 440 Login Time-out\r\n"
            response += f"Content-Type: application/json\r\n"
            response += f"Content-Length: {len(response_body)}\r\n"
            response += "\r\n"
            response += response_body
            return response
        
        else:
            response_data = {
            'status': 'Error: Unknown Error'
            }
            response_body = json.dumps(response_data)

            response = "HTTP/1.1 520 Unknown Error\r\n"
            response += f"Content-Type: application/json\r\n"
            response += f"Content-Length: {len(response_body)}\r\n"
            response += "\r\n"
            response += response_body
            return response
    
    def linkDevice(self, addDevid, addPasswd, recv_request):
        addDevid_full = ('Device#' + addDevid)
        checkCreds = self.session.authenticate(addDevid_full, addPasswd)

        if 'AuthSucceed' == checkCreds:
            # Grab source device id fra cookie/session token
            cookieStatus, src_device_id, stdcol_name  = self.session.sessionCookieAuth(recv_request)

            self.mycursor.execute('SELECT linked_device_ID FROM userConfiguration WHERE source_device_ID = %s', (src_device_id,))
            linked_device_ids = self.mycursor.fetchone()

            # Checker om det linked_device_id allerede eksisterer i userConfiguration for src_device_id
            if linked_device_ids and addDevid_full not in linked_device_ids[0].split(','):

                # Tilføj det nye linked device til source device's 'linked device' liste i databasen
                print(f"[+] Linking device ID: {addDevid_full} to {src_device_id}")
                self.mycursor.execute('UPDATE userConfiguration SET linked_device_ID = CONCAT(linked_device_ID, %s) WHERE source_device_ID = %s;', (',' + addDevid_full, src_device_id))
                self.db.commit()

                # Craft Response
                response_data = {
                'status': 'Sensor: Add request succeeded',
                }
                response_body = json.dumps(response_data)

                response = "HTTP/1.1 200 OK\r\n"
                response += f"Content-Type: application/json\r\n"
                response += f"Content-Length: {len(response_body)}\r\n"
                response += "\r\n"
                response += response_body
                return response
        
            else:
                return

        elif 'AuthFailed':
            # Craft Response
            response_data = {
            'status': 'Sensor: Invalid credentials',
            }
            response_body = json.dumps(response_data)

            response = "HTTP/1.1 440 Login Time-out\r\n"
            response += f"Content-Type: application/json\r\n"
            response += f"Content-Length: {len(response_body)}\r\n"
            response += "\r\n"
            response += response_body
            return response
        
        else:
            # Craft Response
            response_data = {
            'status': 'Error: Unknown Error',
            }
            response_body = json.dumps(response_data)

            response = "HTTP/1.1 520 Unknown Error\r\n"
            response += f"Content-Type: application/json\r\n"
            response += f"Content-Length: {len(response_body)}\r\n"
            response += "\r\n"
            response += response_body
            return response

    def getLinkedDevices(self, src_devID):
        linked_dev_ids_list = []

        # Grab linked device's fra src_devID
        self.mycursor.execute('SELECT linked_device_ID FROM userConfiguration WHERE source_device_ID = %s', (src_devID,))
        linked_devices_results = self.mycursor.fetchall()

        for device in linked_devices_results:
            linked_device_ids_str = device[0]

            print(f"\n\n[+] Linked devices to '{src_devID}': {linked_device_ids_str} \n\n")

            print(f"[+] Grabbing linked devices for {src_devID}")
            if linked_device_ids_str:
                linked_dev_ids_list.extend(linked_device_ids_str.split(','))

        linked_dev_ids_list = [device.strip() for device in linked_dev_ids_list if device.strip()]
        return linked_dev_ids_list

    def getLinkedDeviceNames(self, linked_devices_list):
        linked_device_names = []
        for device in linked_devices_list:
            self.mycursor.execute('SELECT renamed_ID FROM userConfiguration WHERE source_device_ID = %s', (device,))
            definedname = self.mycursor.fetchone()

            if definedname and f'{device}=' in definedname[0]:
                
                renamed_id_value = definedname[0].split('=')[1].strip(',')

                linked_device_names.extend(renamed_id_value.split(','))

        return linked_device_names

    def renameDevice(self, trgt_deviceID):
        print(f"[+] Renaming {trgt_deviceID}")
        return

    def keepAliveSession(self, recv_rawdata):
        sessionToken = self.session.getCookieID(recv_rawdata)
        self.session.extendSession(sessionToken)

    def cleanupLoop(self):
        while True:
            self.session.cleanupSession()
            time.sleep(40)

class SessionHandler:
    def __init__(self, database, cursor):
        self.db = database
        self.mycursor = cursor

    def getCurrentTime(self):
        # UTC+1
        return (datetime.now() + timedelta(hours=1)).strftime("%H:%M:%S")

    def authenticate(self, username, password):
        try:
            self.mycursor.execute('SELECT deviceId, passwd FROM device_id WHERE deviceId = %s', (username,))
            result = self.mycursor.fetchone()

            if result and bcrypt.checkpw(password.encode('utf-8'), result[1].encode('utf-8')): 
                return 'AuthSucceed'  # Hvis authentication gik igennem
            else:
                return 'AuthFailed' # Hvis der fejles i authentication
        except Exception as e:
            print('[!] Error in authentication: %s' % e)
            return 'AuthOther'

    def GenerateSessionToken (self, username):
        #Genererer en session token ved brug af secrets. token_hex
        SessionToken = secrets.token_hex(16)
        user_id = secrets.choice(range(10000, 99999))

        print(f"Session ID - {SessionToken}, User ID - {user_id}, Device ID - {username}, Time - {self.getCurrentTime()}")

        return SessionToken, user_id

    def storeSessionToken (self, username, SessionToken, UserId):
            try:
                current_time_str = self.getCurrentTime()
                self.mycursor.execute('INSERT INTO session (session_id, user_id, device_id, last_activity) VALUES (%s,%s,%s,%s)', (SessionToken, UserId, username, current_time_str))
                self.db.commit()
    
                print ('[+] Session Token stored in the database.')
            except Exception as e:
                print('[!] Error storing session in the database: %s' % e)
    
    def sessionCookieAuth(self, recv_rawdata):
        cookie_value = self.getCookieID(recv_rawdata)

        try:
            self.mycursor.execute('SELECT device_id FROM session WHERE session_id = %s', (cookie_value,))
            result = self.mycursor.fetchone()

            if result:
                device_id = result[0]
                self.extendSession(cookie_value)

                return 'AuthSucceed', device_id  # Hvis authentication gik igennem
            else:
                return 'AuthFailed', None # Hvis der fejles i authentication
        except Exception as e:
            print('[!] Error in authentication: %s' % e)
            return 'AuthOther', None

    def getCookieID(self, recv_rawdata):
        cookie_value = ""

        data = recv_rawdata.decode('utf-8')

        print(f"[i] Converted raw data to str in sessionCookieAuth: {data}")

        for line in data.split('\r\n'):
            if 'Cookie:' in line:
                print(f"[+] Found session_id title in received POST")
                cookie_value = line.split('session_id=')[1].strip()
                print('[+] Received Cookie Value:', cookie_value)
                return cookie_value

    def extendSession(self, SessionToken):
        print(f"\n[+] Extending session for: {SessionToken}")
        try:
            self.mycursor.execute('SELECT * FROM session WHERE session_id = %s', (SessionToken,))
            result = self.mycursor.fetchone()

            if result:
                self.mycursor.execute('UPDATE session SET last_activity = %s WHERE session_id = %s', (self.getCurrentTime(), SessionToken))
                self.db.commit()
                return True
            else:
                return False  
        except Exception as e:
            print('[!] Error in extending session: %s' % e)
            return False

    def cleanupSession(self):
        try:
            # Hent alle sessions fra databasen
            self.mycursor.execute('SELECT session_id, last_activity FROM session')
            sessions = self.mycursor.fetchall()

            print(f"Retrived sessions: {sessions}")

            for session in sessions:
                session_id, last_activity_time = session

                last_activity_time = datetime.strptime(str(last_activity_time), "%H:%M:%S")
                print(f"last_activity_time: {last_activity_time}")
                current_datetime = datetime.strptime(str(self.getCurrentTime()), "%H:%M:%S")
                print(f"current_datetime: {current_datetime}")
                time_difference = (current_datetime - last_activity_time).total_seconds()
                print(f"time_difference: {time_difference}")

                if time_difference > 40: # Session ældrer end 40 sekunder, drop it.
                    self.mycursor.execute('DELETE FROM session WHERE session_id = %s', (session_id,))
                    self.db.commit()
                    print(f"[i] Dropped inactive session: {session_id}")

        except Exception as e:
            print('[!] Error in session cleanup: %s' % e)
            print(f"[i] Cleanup of session failed")


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
            cleanup_thread = threading.Thread(target=self.handler.cleanupLoop)

            tcp_thread.start()
            udp_thread.start()
            cleanup_thread.start()

            tcp_thread.join()
            udp_thread.join()
            cleanup_thread.join()

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
        post_data = raw_data
        if b'POST' in raw_data:
            print(f"[+] HTTP POST request recieved from reverse proxy on {client_addr}")
            raw_data = self.handler.http_strip(raw_data)

        client_data_tcp = raw_data.decode('utf-8')

        data_dict_tcp = json.loads(client_data_tcp)
        message_type = data_dict_tcp.get('data', '')

        print(f"[+] Received packet of type '{message_type}' from {client_addr}")

        # Call device ID generation
        if 'device ID request' == message_type:
            device_id, pw = self.handler.device_generation()
            response_data = {'device_id': f'{device_id}', 'password': f'{pw}'}
            print(f"Response data: {response_data}")
            client_socket.send(json.dumps(response_data).encode('utf-8'))
            print("[i] Device ID successfully sent to ESP \n")   

        elif 'login request' == message_type:
            recv_device_id = data_dict_tcp.get('user', '')
            recv_password = data_dict_tcp.get('pass', '')
            response_data = self.handler.login_procedure(recv_device_id, recv_password)
        
            print(f"\n[+] Response data to be sent: {response_data}")
            print(f"[+] Client Socket and Address: {client_socket}, {client_addr}\n")

            client_socket.send(response_data.encode('utf-8'))

        elif 'session authorization' == message_type:
            response_data = self.handler.sessionCookieAuthHandler(post_data)

            print(f"\nResponse data to be sent: {response_data}")
            print(f"Client Socket and Address: {client_socket}, {client_addr}\n")
              
            client_socket.send(response_data.encode('utf-8'))

        elif 'session keep-alive' == message_type:
            self.handler.keepAliveSession(post_data)

        elif 'add sensor request' == message_type:
            addDevid = data_dict_tcp.get('user', '')
            addPasswd = data_dict_tcp.get('pass', '')

            response_data = self.handler.linkDevice(addDevid, addPasswd, post_data)
            client_socket.send(response_data.encode('utf-8'))

        elif 'rename sensor request' == message_type:
            target_deviceID = data_dict_tcp.get('target', '')
            self.handler.renameDevice(target_deviceID)
            
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