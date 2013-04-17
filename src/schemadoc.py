import sys
from pprint import pprint

from ckanext.canada.metadata_schema import schema_description

for ckan_name, pilot_name, field in sorted(schema_description.dataset_all_fields()):
    #print "CKAN NAME {} : PILOT NAME {} : ID {} : DESCRIPTION {}".format(ckan_name, pilot_name, field['id'], field['description'])
    print "{}, {}, {}".format(ckan_name, field['label']['eng'], field['description']['eng'])
    
    


