'''
Created on Jul 15, 2012

@author: david
'''
def get_values_from_init_file(init_file):
    """Read the init file and parse program values into a dictionary"""
    values_dict = {}
    lines = init_file.readlines()
    for line in lines:
        line_splits = line.split(",")
        if len(line_splits) == 2:
            values_dict[line_splits[0].strip()] = line_splits[1].strip()
    return values_dict
