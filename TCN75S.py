from machine import I2C
from machine import Pin
from time import sleep

i2c = I2C(scl=Pin(9), sda=Pin(8), freq=100000)

tcn75s_address = 0x48
#othertcn address = 0x49

#denne kode virker for 9 bit signal, hvilket er standarten for TCN75S
def read_temperature():
    # Read temperature data from TCN75S
    i2c.writeto(tcn75s_address, b'\x00')  # Point to the temperature register (address 0x00)
    time.sleep(0.1)  # Wait for the conversion to complete (adjust as needed)
    temperature_byte = i2c.readfrom(tcn75s_address, 1)[0]  # Read 1 byte of temperature data

    # Convert the byte to a temperature value (assumes 9-bit resolution)
    temperature_raw = temperature_byte >> 7  # Shift to extract the 9-bit value
    temperature_celsius = temperature_raw * 0.5  # Each bit represents 0.5 degrees Celsius

    return temperature_celsius

# Main loop
while True:
    temperature = read_temperature()
    print("Temperature: {:.2f} °C".format(temperature))
    time.sleep(1)  # Adjust the delay as needed