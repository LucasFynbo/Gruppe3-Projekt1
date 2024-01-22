from machine import ADC, Pin
import time

#class for Lm335. it needs a pin_number, and if atten, is not specified it is set to ATTN_11DB
class Lm335:
    def __init__(self, pin_number, attenuation=ADC.ATTN_11DB):
        self.adc_pin = pin_number
        self.adc = ADC(Pin(self.adc_pin))
        self.adc.atten(attenuation)
    #function that reads temperature
    def read_temperature(self):
        #reads from the adc, and saves it in variable adc_vlaue
        adc_value = self.adc.read_uv()
        #converts the adc_value to celsius.
        #the adc reads in μV. the adc's value in mV represents the temperatur is kelvin.
        #we divide by 1000 and minus 273.15 to get the temperature in celsius
        temperature_celsius = adc_value * 0.0001 - 273.15
        return temperature_celsius
    
#this is the function you call in other programs, if you want to recieve the temperatur
def monitor_temperatures():
    #define pins:
    adc_pin3 = 3
    adc_pin4 = 4
    #define the adc pins
    sensor1 = Lm335(adc_pin3)
    sensor2 = Lm335(adc_pin4)

    #reads the temperatur from the sensor and saves it in celsius in the two variables temperature1 and temperature2
    temperature1 = sensor1.read_temperature()
    temperature2 = sensor2.read_temperature()
    #rounds the result to 4 decimals
    Rounded_temp1 = round(temperature1, 4)
    Rounded_temp2= round(temperature2, 4)
            
    print(f"LM335 temp1:", Rounded_temp1, "LM335 temp2:", Rounded_temp2)
    #return the result
    return Rounded_temp1, Rounded_temp2
       
    

# Call function