import socket
import sensor_Connection

esp_ip = sensor_Connection.sensorConnection()

class Sensor:
    def __init__(self):
        self.deviceid_path: str = './deviceid.txt'        


class MySocket:
    def __init__(self):
        self.csocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        srvaddr: str = '79.171.148.173'
        srvport: int = 13371

        self.ssocket_addr = (srvaddr, srvport)

    def send_data(self):
        self.csocket.sendto('request device ID'.encode('utf-8'), self.ssocket_addr)

        device_id = self.csocket.recv(1024).decode('utf-8')
        print(device_id)

if __name__ == "__main__":
    mysocket = MySocket()
