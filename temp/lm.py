from machine import ADC, Pin
import time

class Lm335:
    def __init__(self, pin_number, attenuation=ADC.ATTN_11DB):
        self.adc_pin = pin_number
        self.adc = ADC(Pin(self.adc_pin))
        self.adc.atten(attenuation)
    
    def read_temperature(self):
        adc_value = self.adc.read_uv()
        temperature_celsius = adc_value * 0.0001 - 273.15
        return temperature_celsius

def monitor_temperatures():
    adc_pin3 = 3
    adc_pin4 = 4

    sensor1 = Lm335(adc_pin3)
    sensor2 = Lm335(adc_pin4)

    
    temperature1 = sensor1.read_temperature()
    temperature2 = sensor2.read_temperature()
    Rounded_temp1 = round(temperature1, 4)
    Rounded_temp2= round(temperature2, 4)
            
    print(f"LM335 temp1:", Rounded_temp1, "LM335 temp2:", Rounded_temp2)
    
    return Rounded_temp1, Rounded_temp2
       
    

# Call function