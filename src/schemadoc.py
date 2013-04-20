# coding=utf-8
import os
import tabular as tb


from ckanext.canada.metadata_schema import schema_description
Recs = []
print u'\u2019'.encode('utf-8') 
for ckan_name, pilot_name, field in schema_description.dataset_all_fields():
    description = field['description']['eng']
    #description = field['description']['eng'].replace(u'\u2019','') #Fix bad windows chars
    Recs.append((str(field['id']),description,str(ckan_name),str(pilot_name)))

X = tb.tabarray(records = Recs, names=['ID','Description','CKAN Name','Pilot Name'])
X.saveSV('FieldReport.csv',delimiter='\t')


