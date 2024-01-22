# This file is executed on every boot (including wake-boot from deepsleep)
import esp
esp.osdebug(None)
#import webrepl
#webrepl.start()

#calls calibrate program, that ensures that the I2C connection works
import TCN75_calibrate
#calls the program that measures temperatur and saves the result in file
import TCN75_forsog_vask