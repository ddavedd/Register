import serial
import time
ser = serial.Serial('/dev/ttyACM0',9600)
time.sleep(2)
print "Connected to ttyACM0 serial device (arduino)"

def lcd_output(output1,output2):   
   ser.write(output1)
   time.sleep(1)
   ser.write(output2)
   
lcd_output("The Farm","Westmont")
