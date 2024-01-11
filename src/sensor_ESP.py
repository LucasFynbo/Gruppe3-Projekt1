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

temperature_pipe = x_val
temperature_room = y_val

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
        global temperature_pipe, temperature_room
        self.csocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        srvaddr: str = '79.171.148.173'
        srvport: int = 13371

        self.ssocket_addr = (srvaddr, srvport)
    
        # Temperatur data
        self.temp_pipe = temperature_pipe
        self.temp_room = temperature_room

    def connect_to_srv(self):
        self.csocket.connect(self.ssocket_addr)
        
    def send_data(self, type=None):
        
        if 'device id' == type:
            self.connect_to_server()
            data_packet = {'data': f'{type}'}
            self.csocket.send(json.dumps(data_packet).encode('utf-8'))
            
            response_data = self.csocket.recv(1024).decode('utf-8')
            response_dict = json.loads(response_data)
            self.device_id = response_dict.get('device_id', '')
            print(self.device_id)

        elif 'send recording' == type:
            data_packet = {'data': f'{type}', 'temp_pipe': f'{self.temp_pipe}', 'temp_room': f'{self.temp_room}'}
            self.csocket.send(json.dumps(data_packet).encode('utf-8'))
        else:
            pass

if __name__ == "__main__":
    mysocket = MySocket()
    mysocket.send_data(type='device ID request')
        
    while True:
        joystick = JoystickController(y_axis_pin, x_axis_pin)
        joystick.start()
        mysocket.send_data(type='recording data')

    

