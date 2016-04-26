"""A scale to read weight only"""
import serial
import ScaleError

BYTES_TO_READ = 40
MAX_TRIES = 10

class ABScale(object):
    """An Avery Berkel Scale to be used with POS system"""
    
    def __init__(self, device_address):
        """Start a scale with a given address"""
        try:
            self.ser = serial.Serial(device_address, baudrate=9600,
            bytesize=serial.SEVENBITS, parity=serial.PARITY_EVEN,
            stopbits=serial.STOPBITS_ONE, timeout=.1)
        except serial.SerialException:
            print "Scale not connected at %s" % device_address
            print "Please restart program with scale connected"    
            self.ser = None
            
    
    def is_scale_connected(self):
        """Check to see if a scale is connected"""
        if self.ser is not None:
            return True
        else:
            return False
    
    # Fixed but needs to be added to the rest of the programs        
    def get_weight(self):
         """Get the current weight on the scale in pounds"""
         try_number = 1
         while (try_number < MAX_TRIES):
            # Clear all previous data
            #print self.ser.in_waiting
            self.ser.flushInput()
            self.ser.flushOutput()
            
            weight_code = "W" + chr(0x0D)
            self.ser.write(weight_code)
            bytes_read = self.ser.read(BYTES_TO_READ)
            if len(bytes_read) == 0:
               raise ScaleError.ScaleError("Scale Timed Out")
            else:
               #print bytes_read
               clean_bytes = bytes_read.strip()
               pound_code = clean_bytes.split()
               poundage = pound_code[0][:6]
               print poundage
            try:
               return float(poundage)
            except ValueError:
               print "Error reading value, retrying" 
               try_number += 1
         # If it never reads a valid value, return a scale error  
         raise ScaleError.ScaleError("Unable to read scale")
