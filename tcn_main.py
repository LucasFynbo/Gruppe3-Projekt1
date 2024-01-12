from machine import I2C, Pin
import time
import tcn_library

tcn_library.Config_TCN75_Sensitivity()
while True:
    
    TCN75_term1, TCN75_term2 = tcn_library.TCN75_Read_Temp()
    time.sleep(3)