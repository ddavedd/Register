"""A scale to read weight only"""
import serial
import ScaleError
import time

BYTES_TO_READ = 40
MAX_TRIES = 6

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
         weights_recorded = []
         while (try_number < MAX_TRIES):
            # Clear all previous data
            #print self.ser.in_waiting
            self.ser.flushInput()
            self.ser.flushOutput()
            
            weight_code = "W" + chr(0x0D)
            self.ser.write(weight_code)
            time.sleep(.05)
            bytes_read = self.ser.read(BYTES_TO_READ)
            if len(bytes_read) == 0:
               raise ScaleError.ScaleError("Scale Timed Out")
            else:
               #print bytes_read
               clean_bytes = bytes_read.strip()
               pound_code = clean_bytes.split()
               #print pound_code
               poundage = pound_code[0][:6]
               #print poundage
               weights_recorded.append(poundage)
               try_number = try_number + 1
         print weights_recorded
         clean_weights = [float(w) for w in weights_recorded if not (w[0] == "S" or w[0] == "?")]
         if sum([1 for w in weights_recorded if (w[0] == "S" or w[0] == "?")]) >= 2:
            print "Need to retry weight"
            raise ScaleError.ScaleError("Retry Scale")
         elif max(clean_weights) - min(clean_weights) > 0.015:
            print "Inconsistent weights"
            print clean_weights
            print max(clean_weights) - min(clean_weights)
            raise ScaleError.ScaleError("Inconsistent Weights")
         else:
            print "Average reading"
            average = sum(clean_weights)/float(len(clean_weights))
            print average
            return average
