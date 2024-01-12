from machine import Pin, ADC
import socket
import sensor_Connection
import time
import ujson as json

esp_ip = sensor_Connection.sensorConnection()

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

class MySocket:
    def __init__(self):
        srvaddr: str = '79.171.148.173'
        srvport: int = 13371

        self.ssocket_addr = (srvaddr, srvport)
        
        self.joystick = JoystickController(y_axis_pin, x_axis_pin)

    def connect_to_srv(self):
        csocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        csocket.connect(self.ssocket_addr)
        return csocket
        
    def send_data(self, type=None):
            try:
                if 'device ID request' == type:
                    self.csocket = self.connect_to_srv()
                    data_packet = {'data': f'{type}'}
                    self.csocket.send(json.dumps(data_packet).encode('utf-8'))

                    response_data = self.csocket.recv(1024).decode('utf-8')
                    response_dict = json.loads(response_data)
                    self.device_id = response_dict.get('device_id', '')
                    print(self.device_id)

                elif 'recording data' == type:
                    try:
                        if self.csocket.fileno() == -1:
                            self.csocket = self.connect_to_srv()

                        temperature_pipe, temperature_room = self.joystick.read_joystick()

                        print(temperature_pipe, temperature_room)
                        data_packet = {'data': f'{type}', 'temp_pipe': f'{temperature_pipe}', 'temp_room': f'{temperature_room}'}
                        print(f"Sending data: {json.dumps(data_packet)}")
                        self.csocket.send(json.dumps(data_packet).encode('utf-8'))
                        print("Temperature packet sent")

                    # Current erroring rate: 50%
                    except OSError as e:
                        print(f"Error sending recording data: {e}")
                        if self.csocket.fileno() != -1:
                            self.csocket.close()
                        pass

            except Exception as e:
                print(f"Unhandled exception: {e}")
                
if __name__ == "__main__":
    mysocket = MySocket()
    mysocket.send_data(type='device ID request')

    while True:
        mysocket.send_data(type='recording data')
        time.sleep(1)
