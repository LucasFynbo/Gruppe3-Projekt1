from machine import Pin, ADC
import socket
import sensor_Connection
import time
import ujson as json
import tcn

class MySocket:
    def __init__(self):
        srvaddr: str = '79.171.148.173'
        srvport_tcp: int = 13371 # TCP for device id requesting
        srvport_udp: int = 31337 # UDP for sending af målingsdata

        self.srvcon_tcp = (srvaddr, srvport_tcp)
        self.srvcon_udp = (srvaddr, srvport_udp)

        self.csocket_udp = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

        # Kontroller om der allerede er generet et device ID for ESP'en
        try:
            with open('device_id.txt', 'r') as file:
                credentials_file = file.read()
            
            # Hvis filen er tom
            if '' == credentials_file:
                print("[!] Device ID file empty, requesting...")
                self.send_data(type='device ID request')
            # Hvis Device ID'et allerede er skabt for ESP'en
            else:
                for line in credentials_file.split('\n'):
                    if "DeviceID:" in line:
                        self.device_id = line.split(':')[1].strip()
                print(f"[+] Device ID: {self.device_id}")
        except OSError as e:
            # Hvis filen ikke eksisterer
            if errno.ENOENT == e.errno:
                print("[!] Device ID does not exist, requesting...")
                self.send_data(type='device ID request')
            # Andre errors
            else:
                print("[!] Error: '%s' occured." % e)

    def initTCP_sock(self) -> socket:
        csocket_tcp = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        csocket_tcp.connect(self.srvcon_tcp)
        return csocket_tcp
        
    def send_data(self, type=None):
            try:
                if 'device ID request' == type:
                    csocket_tcp = self.initTCP_sock()
                    data_packet = {'data': f'{type}'}
                    csocket_tcp.send(json.dumps(data_packet).encode('utf-8'))

                    response_data = csocket_tcp.recv(1024).decode('utf-8')
                    response_dict = json.loads(response_data)
                    self.device_id = response_dict.get('device_id', '')
                    self.password = response_dict.get('password', '')
                    print(f"[i] Device ID recieved: {self.device_id} \n")
                    print (f"[i] Password recieved: {self.password} \n")

                    csocket_tcp.close()

                    # Gem det genereret device id og password til 'device_id.txt'
                    with open('device_id.txt', 'w') as file:
                        file.write(f"DeviceID:{self.device_id}\nPassword:{self.password}")

                elif 'recording data' == type:
                        temperature_pipe, temperature_room = tcn.TCN75_Read_Temp()

                        print(f"[+] Read temperature: {temperature_pipe}, {temperature_room}")
                        data_packet = {'data': f'{type}', 'device_id': f'{self.device_id}','temp_pipe': f'{temperature_pipe}', 'temp_room': f'{temperature_room}'}
                        print(f"[+] Sending data: {json.dumps(data_packet)}")
                        self.csocket_udp.sendto(json.dumps(data_packet).encode('utf-8'), self.srvcon_udp)
                        print("Temperature packet sent")

            except Exception as e:
                print(f"Unhandled exception: {e}")
                
if __name__ == "__main__":
    esp_ip = sensor_Connection.sensorConnection()    
    tcn.Config_TCN75_Sensitivity()
    
    mysocket = MySocket()

    while True:
        mysocket.send_data(type='recording data')
        time.sleep(30)
