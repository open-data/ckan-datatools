'''
    Pseudo Code for Data Cleansing:
    
    For every record node:
    0. Check to see if any required fields are missing.  If so, log it. 
    1. Replace  codes with actual names. If the code is missing, log it.
    2. For every field mapping, add value to json dictionary.
    3. Add default values. 
    
    OR//
    
    For each field in record:
    If missing, log it or provide defualt.
    If Code, replace with value
    Finally, add default values. 
    

'''
from pprint import pprint
from ckanext.canada.metadata_schema import schema_description



if __name__ == "__main__": 
    all_resource_fields = set(ckan_id
                     for ckan_id, ignore, field
                     in schema_description.resource_fields_by_ckan_id(include_existing=True))
    

    
    extra_resource_fields = set(ckan_id
                     for ckan_id, ignore, field
                     in schema_description.resource_fields_by_ckan_id(include_existing=False))
    
    existing_resource_fields = all_resource_fields - extra_resource_fields
    
    print sorted(all_resource_fields)
    print "All %s" % sorted(all_resource_fields)
    print "Extras %s" % sorted(extra_resource_fields)
    print "Existing %s" % sorted(existing_resource_fields)
 
    for field in sorted(schema_description.resource_fields):
        #print field['id']
        pass
        
    for name, lang, field in schema_description.resource_fields_by_ckan_id(True):
        #print((name, lang, id(field)))
        pass

