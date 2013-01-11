'''
Created on 2013-01-10

@author: jakoped

An easy place to read  and access fields mappings from pilot consisting of 
    pilot deparment _id, department acronym, department name
'''
from collections import namedtuple
#Define the data structure
Department =  namedtuple("Department", "id acronym name")




def parse_dept_mappings():
    pass