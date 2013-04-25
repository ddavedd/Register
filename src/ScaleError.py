"""ScaleError is a defined exception used when reading the scale doesn't work"""
class ScaleError(Exception):
    """Thrown when reading the scale doesn't work"""
    def __init__(self, value):
        """Initialize the error with a string"""
        self.value = value
        
    def __str__(self):
        """The string representation of this error"""
        return repr(self.value)