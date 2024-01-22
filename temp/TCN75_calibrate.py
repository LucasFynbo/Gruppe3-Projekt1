from machine import SoftI2C, Pin
from time import sleep
#this code is used to kickstart the I2C procedure
#it takes a single reading of the TCN75
#we had problems where if we started with two I2C devieces at the same time. It would not work
#but this code runs it with one device. And after that the ESP32 is ready for two devices at the same time


# Define your SDA and SCL pins
sda_pin = 8
scl_pin = 9

# Create SoftI2C object with pull-up resistors
i2c = SoftI2C(sda=Pin(sda_pin, Pin.IN, Pin.PULL_UP), scl=Pin(scl_pin, Pin.IN, Pin.PULL_UP))

# Set the correct I2C address for the TCN75A (0x48)
term_address = 0x49

# Configuration register value for 0.125 Celsius resolution
config_register_value = 0x60  # Binary: 0100 0000

try:
    # Write the configuration to the thermometer
    i2c.writeto_mem(term_address, 0x01, bytearray([config_register_value]))
except Exception as e:
    print("Error writing to thermometer:", e)

sleep(0.5)

#import TCN75Calibrate
#import TCN75ForsøgVask

try:
    # Read the temperature value (2 bytes)
    #term_address is the address of the device
    #0x00 is the address for the amibent temperature register(the place that have the temperature)
    #2 is the number of bits we recieve
    data = i2c.readfrom_mem(term_address, 0x00, 2)
        
    # Convert the data to 11-bits
    temp = (((data[0] * 256) + (data[1] & 0xE0)) / 32)
    cTemp = temp * 0.125

    # Print the temperature
    print("Temperature:", cTemp, "°C")

except Exception as e:
    print("Error reading from thermometer:", e)
        