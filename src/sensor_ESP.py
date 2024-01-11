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

    def send_data(self, type = None):
        self.csocket.connect(self.ssocket_addr)
        if 'device id' == type:
            self.csocket.send('request device ID'.encode('utf-8'))

            self.device_id = self.csocket.recv(1024).decode('utf-8')
            print(self.device_id)
        elif 'send recording' == type:
            data_packet = self.craft_packet()
            self.csocket.send(data_packet.encode('utf-8'))

    def craft_packet(self):
        # indhent x_value og y_value

        packet = """recording data {
            'device_id': %s
            'temperature_room': %d
            'temperature_pipe': %d
        }""" % (self.device_id, x_value, y_value)
        return packet

if __name__ == "__main__":
    mysocket = MySocket()
    mysocket.send_data(type='device id')
    mysocket.send_data(type='send recording')
