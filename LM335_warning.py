from machine import ADC, Pin
import time

# Importerer output fra temperatur sensorere 
class Lm335:
    def __init__(self, pin_number, attenuation=ADC.ATTN_11DB):
        self.adc_pin = pin_number
        self.adc = ADC(Pin(self.adc_pin))
        self.adc.atten(attenuation)
    
    def read_temperature(self):
        adc_value = self.adc.read_uv()
        temperature_celsius = adc_value * 0.0001 - 273.15
        return temperature_celsius

# Henviser til PINs på ESP32 
adc_pin3 = 3
adc_pin4 = 4

sensor1 = Lm335(adc_pin3)
sensor2 = Lm335(adc_pin4)

while True:
    # Læser output fra sensorerne 
    temperature1 = sensor1.read_temperature()
    temperature2 = sensor2.read_temperature()
        
    # Skriver temperatur forskel, samt temperatur for de to sensorer
    temperature_difference = abs(temperature1 - temperature2)
    rund_temperature_difference = round(temperature_difference, 2)
    print(f"Temperatur forskel:", rund_temperature_difference, "Vandrør temp:", temperature1, "Rum temp:", temperature2)

    # Grænseværdi for temperatur forskel
    temp_threshold = 3
    
    # Skriver advarsel hvis grænseværdien overskrides
    if temperature_difference > temp_threshold:
        print(f"!!! Advarsel: Temperatur forskel mere end {temp_threshold} grader !!!")
    
    # Tid mellem hver print output
    time.sleep(2)
