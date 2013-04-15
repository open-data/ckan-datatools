from ckanext.canada.metadata_schema import schema_description

for ckan_name, pilot_name, field in schema_description.dataset_all_fields():
    print "CKAN NAME {} : PILOT NAME {} : ID {} : DESCRIPTION {}".format(ckan_name, pilot_name, field['id'], field['description']['id'])


