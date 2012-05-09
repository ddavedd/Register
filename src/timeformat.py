"""The time format we are using for timestamps"""
from datetime import datetime

def get_time_format_string():
    """Get the format of the time"""
    return "%Y %m %d %H %M %S"


def get_timestamp_string():
    """Get the timestamp of the current time and date"""
    return datetime.strftime(datetime.now(), get_time_format_string())
