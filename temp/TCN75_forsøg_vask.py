from machine import I2C, Pin
import time
import tcn1

tcn1.Config_TCN75_Sensitivity()
while True:
    
    TCN75_term1, TCN75_term2 = tcn1.TCN75_Read_Temp()
    
    with open('TestTCN75', 'a') as file:
        # Write the output to the file
        file.write('Term 1: {}\nTerm 2: {}\n'.format(TCN75_term1, TCN75_term2))
    file.close
    time.sleep(600)