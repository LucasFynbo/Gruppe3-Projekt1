from machine import I2C, Pin
import time

#This program reads the temperatur of two TCN devices and prints the result in the terminal

# Create SoftI2C object
i2c = I2C(scl=Pin(9), sda=Pin(8), freq=100000)

# Set the correct I2C addresses for the TCN75A thermometers
term_address_1 = 73 #0x49
term_address_2 = 72 #0x48

# Configuration register value for 0.125 Celsius resolution
config_register_value = 0x60  # Binary: 0110 0000

try:
    # Write the configuration to the thermometers
    i2c.writeto_mem(term_address_1, 0x01, bytearray([config_register_value]))
    i2c.writeto_mem(term_address_2, 0x01, bytearray([config_register_value]))
except Exception as e:
    print("Error writing to thermometers:", e)

time.sleep(0.5)
while True:
    try:
        # Read the temperature values from both thermometers (2 bytes each)
        data_1 = i2c.readfrom_mem(term_address_1, 0x00, 2)
        data_2 = i2c.readfrom_mem(term_address_2, 0x00, 2)
        
        # Convert the data to 11-bits for thermometer 1
        temp_1 = (((data_1[0] * 256) + (data_1[1] & 0xE0)) / 32)
        cTemp_1 = temp_1 * 0.125

        # Convert the data to 11-bits for thermometer 2
        temp_2 = (((data_2[0] * 256) + (data_2[1] & 0xE0)) / 32)
        cTemp_2 = temp_2 * 0.125

        # Print the temperatures
        print("Temperature 1:", cTemp_1, "°C")
        print("Temperature 2:", cTemp_2, "°C")

    except Exception as e:
        print("Error reading from thermometers:", e)
        
    time.sleep(5)