'''
Created on 2013-01-10

@author: jakoped

An easy place to read  and access fields mappings from pilot consisting of 
    pilot deparment _id, department acronym, department name
'''
from collections import namedtuple


class Level:
    'A list field hierarchy types'
    PACKAGE = 'package'
    RESOURCE = 'resource'
    EXTRA = 'extra'


# I could also just make lists and then make sets out of them?

class Type:
    'A list of system requirements types'
    AUTO = 'ckan_auto'
    REQUIRED = 'ckan_required'
    OPTIONAL = 'ckan_optional'
    

Field = namedtuple("Field", "level ckan pilot schema type default example")
fields = [
          #Field(Level.PACKAGE,"id", "uniqueformid", "File Identifier", Type.OPTIONAL, "", "25576558-e95b-4496-bcd2-60cc34251888"),
          Field("package","name", "thisformid", "uri", Type.REQUIRED , "", "my-report"),
          Field("package","title", "title_en", "", "","",  ""),
          Field("package","version", 	"", "", "","",  ""),
          Field("package","author", "", "", "","",  ""),
          Field("package","author_email", "contact_email", "", "", "", ""),
          Field("package","maintainer", "", "", "", "", ""),
          Field("package","maintainer_email", "owner", "","",  "", ""),
          Field("package","notes", "", "", "", "", ""),
          Field("package","license_id", "", "", "", "", ""),
          Field("package","type", "", "", "", "", ""),
		  Field("package","state", "", "", "","",  ""),
	  	  Field("package","revision_id", "", "", "", "", ""),
	 	  Field("package","license", "", "", "", "", ""),
	 	  Field("package","isopen", "", "", "", "", ""),
	 	  Field("package","tags", "", "", "", "", ""),
	 	  Field("package","groups", "department", "", "", "", "['statcan']"),
	 	  Field("package","extras", "", "", "", "", ""),
	 	  Field("package","ratings_average", "", "", "", "", ""),
	 	  Field("package","ratings_count", "", "", "", "", ""),
	 	  Field("package","resources**", "", "", "", "", ""),
	 	  Field("package","ckan_url", "", "", "", "", ""),
	 	  Field("package","relationships", "", "", "", "", ""),
	 	  Field("package","metadata_modified", "", "", "", "", ""),
	 	  Field("package","metadata_created", "", "", "", "", ""),
	 	  Field("package","notes_rendered", "", "", "", "", ""),
	 	  Field("package","tracking_summary", "", "", "", "", ""),
		 
		 
#          Field("resource","type", "", "", "","",""),
#          Field("resource","", "", "", "","",  ""),
#          Field("resource","", "", "", "","",  ""),
#          Field("resource","", "", "", "", "", ""),
#          Field("extra","", "", "", "","", "",""),
#          Field("extra","", "", "", "","", "",""),
#          

         ]

# give me all the ckan names that exists for pilot names that are not empty
ckan_pilot_common = { (f.ckan,f.pilot) for f in fields if f.pilot != '' }

ckan_package_fieldnames = { b.ckan for b in fields if b.level == 'package'}
