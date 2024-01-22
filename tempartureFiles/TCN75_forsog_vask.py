from machine import I2C, Pin
import time
import tcn as tcn

#calls config registor of TCN75 and changes resolution of the themometers to 0.125°C
tcn.Config_TCN75_Sensitivity()
while True:
    #calls the temperatur read function from tcn and saves the result in TCN75_term1 and TCN75_term2
    TCN75_term1, TCN75_term2 = tcn.TCN75_Read_Temp()
    
    #writes and saves the result of the two thermometers in the file TestTCN75.
    with open('TestTCN75', 'a') as file:
        # Write the output to the file
        file.write('Term 1: {}\nTerm 2: {}\n'.format(TCN75_term1, TCN75_term2))
    file.close
    time.sleep(600)