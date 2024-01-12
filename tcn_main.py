from machine import I2C, Pin
import time
import tcn_library

tcn1.Config_TCN75_Sensitivity()
while True:
    
    TCN75_term1, TCN75_term2 = tcn1.TCN75_Read_Temp()
    time.sleep(3)