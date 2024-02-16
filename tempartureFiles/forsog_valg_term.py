from machine import I2C, Pin
import time
#driver of TCN75
import tcn
#driver of LM335
import lm

#calls config registor of TCN75 and changes resolution of the themometers to 0.125°C
tcn.Config_TCN75_Sensitivity()

while True:
    #This calls the tcn.TCN75_Read_Temp() function and saves the
    TCN75_term1, TCN75_term2 = tcn.TCN75_Read_Temp()
    
    with open('ResultatTCN75', 'a') as file:
        # Write the output to the file
        file.write('Term 1: {}°C\nTerm 2: {}°C\n'.format(TCN75_term1, TCN75_term2))
    file.close
    
    LM335_term1, LM335_term2 = lm.monitor_temperatures()
    
    with open('ResultatLM335', 'a') as file:
        # Write the output to the file
        file.write('Term 1: {}°C\nTerm 2: {}°C\n'.format(LM335_term1, LM335_term2))
    file.close
    time.sleep(5)

    