from machine import I2C, Pin
import time
import tcn1
import lm1

tcn1.Config_TCN75_Sensitivity()
while True:
    
    TCN75_term1, TCN75_term2 = tcn1.TCN75_Read_Temp()
    
    with open('ResultatTCN75', 'a') as file:
        # Write the output to the file
        file.write('Term 1: {}°C\nTerm 2: {}°C\n'.format(TCN75_term1, TCN75_term2))
    file.close
    
    LM335_term1, LM335_term2 = lm1.monitor_temperatures()
    
    with open('ResultatLM335', 'a') as file:
        # Write the output to the file
        file.write('Term 1: {}°C\nTerm 2: {}°C\n'.format(LM335_term1, LM335_term2))
    file.close
    time.sleep(5)

    