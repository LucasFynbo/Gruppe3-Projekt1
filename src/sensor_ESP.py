import socket
import sensor_Connection
from machine import Pin, ADC
import time
import ujson as json

esp_ip = sensor_Connection.sensorConnection()

x_val = 0
y_val = 0
y_axis_pin = 2
x_axis_pin = 3

class Sensor:
    def __init__(self):
        self.deviceid_path: str = './deviceid.txt'        

class JoystickController:
    def __init__(self, y_axis_pin, x_axis_pin):

        self.y_axis_pin = y_axis_pin
        self.x_axis_pin = x_axis_pin

        self.y_axis = ADC(Pin(self.y_axis_pin, Pin.IN), atten=ADC.ATTN_11DB)
        self.x_axis = ADC(Pin(self.x_axis_pin, Pin.IN), atten=ADC.ATTN_11DB)

    def read_joystick(self):
        y_value = self.y_axis.read()
        x_value = self.x_axis.read()
        return y_value, x_value

    def start(self):
        global x_val, y_val
        x_val, y_val = self.read_joystick()
        print("X-Axis: {}, Y-axis: {}".format(x_val, y_val))
        time.sleep(0.1)

class MySocket:
    def __init__(self):
        self.csocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        srvaddr: str = '79.171.148.173'
        srvport: int = 13371

        self.ssocket_addr = (srvaddr, srvport)
<<<<<<< HEAD

    def send_data(self, type = None):
        if 'device id' == type:
            self.csocket.send('request device ID'.encode('utf-8'))

            self.device_id = self.csocket.recv(1024).decode('utf-8')
            print(self.device_id)
        elif 'send recording' == type:
            data_packet = self.craft_packet()
            self.csocket.send(data_packet.encode('utf-8'))
        self.ssocket_addr.close()
    def craft_packet(self):
        # indhent x_value og y_value

        packet = f"""recording data {
            'device_id': %s
            'temperature_room': %d
            'temperature_pipe': %d
        }""" % (self.device_id, x_value, y_value)
=======
        
    def connect_to_srv(self):
        self.csocket.connect(self.ssocket_addr)
        
    def send_data(self, data_type=None):
        
        if 'device id' == data_type:
            self.connect_to_server()
            request_data = {'request': 'device ID'}
            self.csocket.send(ujson.dumps(request_data).encode('utf-8'))
            
            response_data = self.csocket.recv(1024).decode('utf-8')
            response_dict = ujson.loads(response_data)
            self.device_id = response_dict.get('device_id', '')
            print(self.device_id)
        elif 'send recording' == type:
            data_packet = self.craft_packet()
            self.csocket.send(ujson.dumps(data_packet).encode('utf-8'))
        else:
            pass

    def craft_packet(self):
        # indhent x_value og y_value
        global x_val, y_val
        print(x_val, y_val)
        
>>>>>>> 05742b363e8cdeece0d4e0977133827181bbcc86
        return packet

if __name__ == "__main__":
    mysocket = MySocket()
    mysocket.send_data(type='device id')
        
    while True:
        joystick = JoystickController(y_axis_pin, x_axis_pin)
        joystick.start()
        mysocket.send_data(type='send recording')

    

