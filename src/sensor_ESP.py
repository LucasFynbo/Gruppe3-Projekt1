from machine import ADC, Pin
import time

# Access Point class



class Lm335:
        def __init__(self, pin_number, attenuation=ADC.ATTN_11DB):
            self.adc_pin= pin_number
            self.adc = ADC(Pin(self.adc_pin))
            self.adc.atten(attenuation)
        
        def read_temperature(self):
            adc_value = self.adc.read_uv()
            temperature_celsius = adc_value*0.0001 - 273.15
            return temperature_celsius


def main():
    adc_pin3 = 3
    adc_pin4 = 4

    sensor1 = Lm335(adc_pin3)
    sensor2 = Lm335(adc_pin4)

    while True:
        temperature1 = sensor1.read_temperature()
        temperature2 = sensor2.read_temperature()
        
        print ("temp 1 i celsius:", temperature1)
        print("temp 2 i celsius", temperature2)
        
        time.sleep(1)

if __name__ == "__main__":
    main()