import bcrypt #Modul til saltning og hashing
import mysql.connector # MySQL database connection module
import socket, errno 
from datetime import datetime, timedelta
import json
import threading
import secrets # Modul til generering af stærke kryptografiske passwords
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
            pw = secrets.token_urlsafe(8) #Passwordet skabes, dette bruger kunden til login.
            hashPass = bcrypt.hashpw(pw.encode('utf-8'), bcrypt.gensalt()) # Passwordet bliver saltet og hashet, dette opbevares i databasen.
            rtal = secrets.choice(range(10000, 99999)) # Device id skabes, dette er en blot en streng af tal.
            device_id = ('Device#' + str(rtal))

            # Tjek MySQL db om der et device id som er i forvejen genereret. 
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
        
    #Alarmsystemet          
    def alarm(self, srcDeviceId):
        try: 
            self.mycursor.execute('SELECT temp_pipe, temp_room FROM tempreadings WHERE device_id = %s', (srcDeviceId,)) #Tager målinger fra de 2 sensorer fra databasen, gemmer det i readings.
            readings = self.mycursor.fetchall()

        #Udregning af gennemsnit
            if len(readings) > 1:
                tempDifs = [abs(readings[i][0] - readings [i][1]) for i in range (1, len (readings))] #Beregner temperaturforskelle mellem hver aflæsning vha. lister. abs() sørger for at det ikke bliver negativt.
                avgDif = sum (tempDifs) / len (tempDifs) # Her udregnes gennesnittet og gemmer det i avgDif
                avgDif = "{:.2f}".format(avgDif)
            print(f'[i] Average Temperature Difference: {avgDif}')
        
            alarmThreshold = 3 #Tolerancen for temperatur forskel

            if float(avgDif) > int(alarmThreshold): #hvis gennemsnitsforskellen er større end tolerancen
                print (f"[!] Alarm Triggered! Average temperature exceeds threshold: {avgDif}")
                
                #Indsæt i mysql loggen at alarm er triggered
                logMsg = f" Alarm triggered for {srcDeviceId}. Average temperature difference: {avgDif}"
                self.mycursor.execute('INSERT INTO log (device_id, alarmtype) VALUES (%s,%s)', (srcDeviceId, logMsg))
                self.db.commit()
                print("[i] Log entry added.")

        except Exception as e:
            print ('[!] Error in calculating average temperature difference: %s' % e)
            return None

    # Handler af målingsdata fra vandspildsmåleren
    def recordingdata_handler(self, device_id="NULL", temp_pipe=0, temp_room=0):
        #Laver målingerne om til float, den kommer ind som en string
        temp_pipe = float(temp_pipe) 
        temp_room = float(temp_room)
        
        try:
            temp_diff = abs(temp_pipe - temp_room)
        #Sætter både device id, temperaturer og temperaturforskelle ind i databasen.
            self.mycursor.execute('INSERT INTO tempreadings (device_id, temp_pipe, temp_room, temp_diff) VALUES (%s,%s,%s,%s)', (device_id, temp_pipe, temp_room, temp_diff)) 
            self.db.commit()
            self.alarm(device_id)
            print('[+] Successfully added Temperature entry for %s \n' % device_id)
        except Exception as e:
            print('[!] Encountered exception error while adding temperature entry: %s' % e)
    
    # Login request handler
    def login_procedure(self, username, password):
        device_id = ('Device#' + username)

        login_status = self.session.authenticate(device_id, password)

        if 'AuthSucceed' == login_status:
            SessionToken, UserId = self.session.GenerateSessionToken(device_id) #Hvis login er gennemført, bliver et SessionToken genereret og givet til klienten. 
            print (f"[+] Session Token for {device_id}: {SessionToken}") 

            self.session.storeSessionToken(device_id, SessionToken, UserId) #Lagrer det genererede SessionToken 
            # Gør cookie header og body klar
            set_cookie_header = f"Set-Cookie: session_id={SessionToken}; username={device_id}; Secure; HttpOnly\r\n" #
            response_data = {
            'status': 'Login: Credentials accepted'
            }
            response_body = json.dumps(response_data)
            # Konstruering af HTTP respons
            response = "HTTP/1.1 200 OK\r\n"
            response += set_cookie_header
            response += f"Content-Type: application/json\r\n"
            response += f"Content-Length: {len(response_body)}\r\n"
            response += "\r\n"
            response += response_body
            return response
        # Hvis login fejler pga mislykket authentication
        elif 'AuthFailed':
            response_data = {
            'status': 'Error: Invalid credentials'
            }
            response_body = json.dumps(response_data)
            # HTTP respons ved forkerte credentials
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
            #HTTP respons ved ukendt fejl

            response = "HTTP/1.1 520 Unknown Error\r\n"
            response += f"Content-Type: application/json\r\n"
            response += f"Content-Length: {len(response_body)}\r\n"
            response += "\r\n"
            response += response_body
            return response
    # Håndterer session cookie authentication
    def sessionCookieAuthHandler(self, recv_rawdata):
        # Udfører cookie authentication samt status og kilde.
        cookieStatus, src_device_id = self.session.sessionCookieAuth(recv_rawdata)
        # Ser efter om session cookie authentication er vellykket
        if 'AuthSucceed' == cookieStatus:
            #Hvis den er vellykket, modtager den linked devices og deres navne.
            linked_devices = self.getLinkedDevices(src_device_id)
            linked_device_names = self.getLinkedDeviceNames(linked_devices)

            print(f"\n\nTest printing functions: getLinkedDevices: {linked_devices}, \ngetLinkedDeviceNames: {linked_device_names}\n\n")
             
            response_data = {
            'status': 'Session: Authorization confirmed',
        
            'username': f'{src_device_id}',
            'linked_devices': f'{linked_devices}',
            'linked_device_names': f'{linked_device_names}'
            }
            response_body = json.dumps(response_data)
            #HTTP respons hvis authorization er vellykket.
            response = "HTTP/1.1 200 OK\r\n"
            response += f"Content-Type: application/json\r\n"
            response += f"Content-Length: {len(response_body)}\r\n"
            response += "\r\n"
            response += response_body
            return response
        # Fejlet authorization
        elif 'AuthFailed' == cookieStatus:
            response_data = {
            'status': 'Error: Session Time-out'
            }
            response_body = json.dumps(response_data)
            # HTTP respons ved timeout
            response = "HTTP/1.1 440 Login Time-out\r\n"
            response += f"Content-Type: application/json\r\n"
            response += f"Content-Length: {len(response_body)}\r\n"
            response += "\r\n"
            response += response_body
            return response
        # HTTP respons ved ukendt fejl
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
    #Funktion til at linke flere devices sammen
    def linkDevice(self, addDevid, addPasswd, recv_request):
        addDevid_full = ('Device#' + addDevid)
        checkCreds = self.session.authenticate(addDevid_full, addPasswd)

        if 'AuthSucceed' == checkCreds:
            # Grab source device id fra cookie/session token
            cookieStatus, src_device_id  = self.session.sessionCookieAuth(recv_request)

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

        # Grab linked device's fra src_devID i databasen
        self.mycursor.execute('SELECT linked_device_ID FROM userConfiguration WHERE source_device_ID = %s', (src_devID,))
        linked_devices_results = self.mycursor.fetchall()

        for device in linked_devices_results: 
            linked_device_ids_str = device[0] # Finder linked device id ud fra resultatet

            print(f"\n\n[+] Linked devices to '{src_devID}': {linked_device_ids_str} \n\n") # Print info om de linkede devices

            print(f"[+] Grabbing linked devices for {src_devID}") # Tager de linkede devices for source device
            if linked_device_ids_str:
                linked_dev_ids_list.extend(linked_device_ids_str.split(',')) #Udvider listen med linked devices hvis der findes nogle nye.

        linked_dev_ids_list = [device.strip() for device in linked_dev_ids_list if device.strip()] # Rydder op i listen ved at fjerne whitespace
        return linked_dev_ids_list 

    def getLinkedDeviceNames(self, linked_devices_list): # Funktion til at tage linked device navne ud fra en liste af linked device id.
        linked_device_names = []
        
        for device in linked_devices_list: # Looper igennem alle linked device id i listen.
        
            self.mycursor.execute('SELECT renamed_ID FROM userConfiguration WHERE source_device_ID = %s', (device,)) # Finder det renamede id i databasen.
            definedname = self.mycursor.fetchone() # Resultatet fra databasen.

            if definedname and f'{device}=' in definedname[0]: # Tjekker om det omdøbte id er fundet og om det er det forventede format
                
                renamed_id_value = definedname[0].split('=')[1].strip(',') # Tager id'et og stripper det for kommaer

                linked_device_names.extend(renamed_id_value.split(',')) # Udvider listen med linked device navne. 

        return linked_device_names

    def getData(self, recv_request): #Funktion til at indhente data efter en forespørgsel 
        cookieStatus, src_device_id  = self.session.sessionCookieAuth(recv_request) #Godkender ved at kigge på cookie og source device id.
        
        # Get linked devices list
        linked_devices = self.getLinkedDevices(src_device_id)
        linked_device_names = self.getLinkedDeviceNames(linked_devices)

        temperature_data = {} #Oprettelse af dictionaries til opbevaring af temperatur og alarm logs for hver device.
        alarm_logs = {}

        for device in linked_devices: #Looper igennem linked devices for at finde temperatur og alarmdata
            self.mycursor.execute('SELECT temp_diff FROM tempreadings WHERE device_id = %s', (device,))# Finder temperaturen på det nuværende device fra databasen
            device_data_temp = self.mycursor.fetchall()
            temperature_data[device] = [temp[0] for temp in device_data_temp]
            
            self.mycursor.execute('SELECT alarmtype FROM log WHERE device_id = %s', (device,)) # finder alarm logs for den nuværende database
            device_data_alarm = self.mycursor.fetchall()
            alarm_logs[device] = [alarm[0] for alarm in device_data_alarm]

        # Gør data klar til at blive sendt 
        response_data = {
        'status': 'Session: data update',
    
        'linked_devices': f'{linked_devices}',
        'linked_device_names': f'{linked_device_names}',
        'temperature_data': f'{temperature_data}',
        'alarm_logs': f'{alarm_logs}'
        }
        response_body = json.dumps(response_data)
        # HTTP response
        response = "HTTP/1.1 200 OK\r\n"
        response += f"Content-Type: application/json\r\n"
        response += f"Content-Length: {len(response_body)}\r\n"
        response += "\r\n"
        response += response_body
        return response

    # Not implemented yet
    def renameDevice(self, trgt_deviceID):
        print(f"[+] Renaming {trgt_deviceID}")

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
        self.mycursor = cursor #Intialiserer med en connection til databasen

    def getCurrentTime(self):
        # UTC+1 tidszone
        return (datetime.now() + timedelta(hours=1)).strftime("%H:%M:%S")

    def authenticate(self, username, password):
        try:
            self.mycursor.execute('SELECT deviceId, passwd FROM device_id WHERE deviceId = %s', (username,)) #Kigger databasen igennem for det indtastede deviceid og passwd
            result = self.mycursor.fetchone()

            if result and bcrypt.checkpw(password.encode('utf-8'), result[1].encode('utf-8')): # Tjekker om der kommer et resultat, samt om det indtastede password passer med det hashede i databasen
                return 'AuthSucceed'  # Hvis authentication gik igennem
            else:
                return 'AuthFailed' # Hvis der fejles i authentication
        except Exception as e:
            print('[!] Error in authentication: %s' % e)
            return 'AuthOther'

    def GenerateSessionToken (self, username):
        SessionToken = secrets.token_hex(16) #Genererer en session token ved brug af secrets. token_hex
        user_id = secrets.choice(range(10000, 99999))

        print(f"Session ID - {SessionToken}, User ID - {user_id}, Device ID - {username}, Time - {self.getCurrentTime()}")

        return SessionToken, user_id

    def storeSessionToken (self, username, SessionToken, UserId):
            try:
                current_time_str = self.getCurrentTime() # Finder den nuværende tid som en string
                self.mycursor.execute('INSERT INTO session (session_id, user_id, device_id, last_activity) VALUES (%s,%s,%s,%s)', (SessionToken, UserId, username, current_time_str))
                self.db.commit() # Indsætter session information i databasen
    
                print ('[+] Session Token stored in the database.')
            except Exception as e:
                print('[!] Error storing session in the database: %s' % e)
    
    def sessionCookieAuth(self, recv_rawdata): # Finder session token fra den rå data som modtages. 
        cookie_value = self.getCookieID(recv_rawdata)

        try:
            # Finder device id koblet sammen med session ved at kigge efter i databasen.
            self.mycursor.execute('SELECT device_id FROM session WHERE session_id = %s', (cookie_value,))
            result = self.mycursor.fetchone()

            if result:
                device_id = result[0]
                self.extendSession(cookie_value) #Hvis der kommer et device id fra resultatet, bliver session forlænget.

                return 'AuthSucceed', device_id  # Hvis authentication gik igennem
            else:
                return 'AuthFailed', None # Hvis der fejles i authentication
        except Exception as e:
            print('[!] Error in authentication: %s' % e)
            return 'AuthOther', None

    def getCookieID(self, recv_rawdata):
        cookie_value = "" # Tom string til at opbevare den cookie værdi som bliver udlæst

        data = recv_rawdata.decode('utf-8') # Dekoder den rå data som kommer ind. 

        print(f"[i] Converted raw data to str in sessionCookieAuth")

        for line in data.split('\r\n'): # Kigger igennem hver linje i string repræsentation om der findes 'Cookie' 
            if 'Cookie:' in line: 
                print(f"[+] Found session_id title in received POST")
                cookie_value = line.split('session_id=')[1].strip() # Udlæser værdien af session id cookie
                print('[+] Received Cookie Value:', cookie_value) # Print cookie value
                return cookie_value

    def extendSession(self, SessionToken):
        print(f"\n[+] Extending session for: {SessionToken}")
        try:
            self.mycursor.execute('SELECT * FROM session WHERE session_id = %s', (SessionToken,)) # Kigger databasen igennem for at se om en sesssion med den pågældende session id eksisterer.
            result = self.mycursor.fetchone()

            if result:
                self.mycursor.execute('UPDATE session SET last_activity = %s WHERE session_id = %s', (self.getCurrentTime(), SessionToken)) # Opdateterer sidste aktivtet fra klienten i databasen.
                self.db.commit()
                return True # Hvis session bliver forlænget
            else:
                return False # Hvis der ikke er fundet en session token 
        except Exception as e: 
            print('[!] Error in extending session: %s' % e)
            return False

    def cleanupSession(self):
        try:
            self.mycursor.execute('SELECT session_id, last_activity FROM session') # Hent alle sessions fra databasen
            sessions = self.mycursor.fetchall()

            print(f"Retrived sessions: {sessions}")

            for session in sessions: # Kigger alle sessions igennem i de indhentede sessions
                session_id, last_activity_time = session

                last_activity_time = datetime.strptime(str(last_activity_time), "%H:%M:%S") # Konverterer sidste aktivitet til datetime-objekt
                print(f"last_activity_time: {last_activity_time}")
                current_datetime = datetime.strptime(str(self.getCurrentTime()), "%H:%M:%S") # Find den nuværende tid
                print(f"current_datetime: {current_datetime}")
                time_difference = (current_datetime - last_activity_time).total_seconds() # Udregning af tidsforskel 
                print(f"time_difference: {time_difference}")

                if time_difference > 40: # Session ældre end 40 sekunder, drop it.
                    self.mycursor.execute('DELETE FROM session WHERE session_id = %s', (session_id,)) # 
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
        backlog = 5 # Kø til hjemmeside, der kan maksimalt være 5 på ad gangen.

        self.handler = DataHandler()

        self.srv_socket_tcp = socket.socket(socket.AF_INET, socket.SOCK_STREAM) # Opretter TCP Socket
        self.srv_socket_udp = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) # Opretter UDP Socket
        try:
            self.srv_socket_tcp.bind((HOST, PORT_TCP)) # Binder socket sammen med porten.
            self.srv_socket_udp.bind((HOST, PORT_UDP)) # Binder socket sammen med porten.
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

    def start_listening(self): # Opretter udp og tcp forbindelse med threading
            tcp_thread = threading.Thread(target=self.accept_tcp_connections)
            udp_thread = threading.Thread(target=self.accept_udp_connections)
            cleanup_thread = threading.Thread(target=self.handler.cleanupLoop)

            tcp_thread.start()
            udp_thread.start()
            cleanup_thread.start()
            # Venter på at de igangværende threads bliver færdige før at nye threads bliver startet. 
            tcp_thread.join()
            udp_thread.join()
            cleanup_thread.join()

    def accept_tcp_connections(self): # Accepterer TCP forbindelser og håndterer klienter
            while True:
                # Accepter ny TCP forbindelse
                client_socket_tcp, client_addr = self.srv_socket_tcp.accept()

                try:
                    # Håndterer TCP forbindelsen med handle_tcp_connections
                    self.handle_tcp_client(client_socket_tcp, client_addr)
                except Exception as e:
                    print('Error handling TCP client: %s' % e)
                finally:
                    client_socket_tcp.close()

    def accept_udp_connections(self): # Accepterer og håndtere UDP forbindelser
        while True:
            udp_data, udp_client_addr = self.srv_socket_udp.recvfrom(1024)
            try:
                self.handle_udp_data(udp_data, udp_client_addr) # Håndterer udp forbindelsen med handle_udp_connections
            except Exception as e:
                print('Error handling UDP data: %s' % e)

    def handle_tcp_client(self, client_socket, client_addr="?.?.?.?"): # Håndterer TCP klienter og forespørgsler derfra
        raw_data = client_socket.recv(1024) # Modtager råt data fra TCP klient
        post_data = raw_data # Gemmer det rå data
        if b'POST' in raw_data:
            print(f"[+] HTTP POST request recieved from reverse proxy on {client_addr}")
            raw_data = self.handler.http_strip(raw_data) # Hvis forespørgslen er HTTP POST, bliver denne strippet for unødvendig data.
    
        client_data_tcp = raw_data.decode('utf-8') # Decoder det rå data om til UTF-8 format

        data_dict_tcp = json.loads(client_data_tcp) # Omdanner nu data til JSON
        message_type = data_dict_tcp.get('data', '')

        print(f"[+] Received packet of type '{message_type}' from {client_addr}")
    # Her kaldes de forskellige funktioner afhængig af hvilke forespørgsler som kommer på TCP forbindelserne. 
        # Kald device ID generation
        if 'device ID request' == message_type:
            device_id, pw = self.handler.device_generation()
            response_data = {'device_id': f'{device_id}', 'password': f'{pw}'}
            print(f"Response data: {response_data}")
            client_socket.send(json.dumps(response_data).encode('utf-8'))
            print("[i] Device ID successfully sent to ESP \n")   

        elif 'login request' == message_type: # Her udlæses brugernavn og password til login 
            recv_device_id = data_dict_tcp.get('user', '')
            recv_password = data_dict_tcp.get('pass', '')
            response_data = self.handler.login_procedure(recv_device_id, recv_password)
        
            print(f"\n[+] Response data to be sent: {response_data}")
            print(f"[+] Client Socket and Address: {client_socket}, {client_addr}\n")

            client_socket.send(response_data.encode('utf-8'))

        elif 'session authorization' == message_type: # Hvis forespørgslen er session authorization, sættes denne funktion i gang
            response_data = self.handler.sessionCookieAuthHandler(post_data)

            print(f"\nResponse data to be sent: {response_data}")
            print(f"Client Socket and Address: {client_socket}, {client_addr}\n")
              
            client_socket.send(response_data.encode('utf-8'))

        elif 'session keep-alive' == message_type: # Keep alive funktion sættes igang ved forespørgsel
            self.handler.keepAliveSession(post_data)
        
        elif 'session get data' == message_type: # Session get data sættes i gang ved forespørgsel
            response_data = self.handler.getData(post_data)

            client_socket.send(response_data.encode('utf-8'))
        elif 'add sensor request' == message_type: # Hvis forespørgsel er add sensor, igangsættes de nødvendige funktioner
            addDevid = data_dict_tcp.get('user', '')
            addPasswd = data_dict_tcp.get('pass', '')

            response_data = self.handler.linkDevice(addDevid, addPasswd, post_data)
            client_socket.send(response_data.encode('utf-8'))

        elif 'rename sensor request' == message_type: # Rename sensor funktoner
            target_deviceID = data_dict_tcp.get('target', '')
            self.handler.renameDevice(target_deviceID)
        else:
            print("[!] Error: Unrecognized message type.")
        
    def handle_udp_data(self, udp_data, udp_client_addr): # Her håndteres UDP data som kommer ind, dette er dog kun målinger som håndteres yderligere af recordingdata_handler
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

    def close(self): # Forbindelserne bliver lukket
        self.srv_socket_tcp.close()
        self.srv_socket_udp.close()

if __name__ == "__main__": # Dette betyder at scriptet kun kan startes ved at køre det selvstændigt, det kan fx ikke importeres. 
    comsocket = SocketCommunication()
    comsocket.start_listening()