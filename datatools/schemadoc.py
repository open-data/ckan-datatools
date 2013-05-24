# coding=utf-8
import os
import tabular as tb
from prettytable import PrettyTable

from ckanext.canada.metadata_schema import schema_description

def table():
    Recs = []
    t = PrettyTable(['No.','CKAN Name','Description','Pilot Name'])
    t.align["City name"] = "l" # Left align city names
    t.padding_width = 1 # One space between column edges and contents (default)
    print u'\u2019'.encode('utf-8') 
    for i, (ckan_name, pilot_name, field) in enumerate(schema_description.dataset_all_fields()):
        description = field['description']['eng']
        #description = field['description']['eng'].replace(u'\u2019','') #Fix bad windows chars
        t.add_row([i,str(ckan_name),
                     description,
                     str(pilot_name)
                     ])
    t.align='l'
    print t
#    X = tb.tabarray(records = Recs, names=['ID','Description','CKAN Name','Pilot Name'])
#    X.saveSV('FieldReport.csv',delimiter='\t')


table()
class MarkdownTable:
     
    def __init__(self):
        print "Creating Markdown Table"
    def header(self, headers):
        
        print "---------- {} ----------".format(n)