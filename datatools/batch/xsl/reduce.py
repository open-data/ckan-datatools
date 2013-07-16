#-*- coding:UTF-8 -*-

import sys
import os
from lxml import etree
from lxml import objectify
from datatools import helpers
import simplejson as json
from pprint import pprint
from string import Template
import xmltodict as xmltodict
from collections import OrderedDict
from pkgutil import  simplegeneric

''' Reducing complex XML files to something more simple '''


url_patterns={'.csv':'CSV',
              '.kmz':'kml / kmz',
              '.html':'HTML',
              '.ext':'exe',
              'FORMAT=image/png':'png',
              'www.ec.gc.ca/indicateurs-indicators/default.asp?':'HTML',
              'http://www.ec.gc.ca/data_donnees/SSB-OSM_BioHab/':'CSV',
              'http://maps-cartes.ec.gc.ca/ArcGIS/rest/services/CESI_AirEmissions_NOx/MapServer':"JSON",
              'TableView.aspx?':'HTML'
 
              }

frequency_mappings={"annually":"Annually | Annuel",
                       "asNeeded":"As Needed | Au besoin",
                       "continual":"Continual | Continue",
                       "quarterly":"Quarterly | Trimestriel",
                       "unknown":"Unknown | Inconnu",
                       "weekly":"Weekly | Hebdomadaire"}

def update_frequency(context, codename):
    try:
        return frequency_mappings[codename[0]]
    except:
        return "Unknown | Inconnu"

def format_from_url(context, u):
    
    try:
        url = u[0]
    except:
        return "other"
    for key,value in url_patterns.iteritems():
 
        if key in url:
            return value
               
    return "other"

def size_from_name(context, name):

    try:
        name = name[0]
    except:
        return ""
    
    try:
        size=''
        if  " Kb)" in name:
            size = name.split(' Kb)')[0].split(" - ")[1].strip()
            size = int(size)*1000
        elif " Ko)" in name:
            size =name.split(' Ko)')[0].split(" - ")[1].strip()
            size = int(size)*1000
        elif " B)" in name:
           size =name.split(' B)')[0].split(" - ")[1].strip()
        elif " O)" in name:
            size =name.split(' O)')[0].split(" - ")[1].strip()
        else:
            return ""
        if size=="7,29":
            return "7290"
        elif size=="6.41":
            return "6410"
        return size.round()
    except:
        return ""

def check_date(context, date):  
   
    try:
        if  "ngoing" in date[0]:
            return ""
        elif date[0]=="2009-12-32":
            return "2009-12-31"
        elif date[0] == "01-01-2011":
            return "2011-01-01"
        elif date[0] == "2009-23-2010":
            return ""
        elif date[0]=="09-23-2010":
            return "2010-09-23"
        elif len(date[0])==4:
            return date[0]+"-01-01"
        else:
            return date[0]
    except IndexError:
        return ""
    
def resource_name_from_name(context,lang,name):
    try:
        if lang=="eng":  
            if " HTML " in name[0]: return "HTML table view and download"
            else: return "Dataset"
        elif lang=="fra":
            if " HTML " in name[0]: return "Vue de tableau HTML et t\u00e9l\u00e9chargement"    
            else: return "Données"
                    
    except:
        if lang=="eng":return "Dataset"
        elif lang=="fra": return "Données"

def resource_type_from_name(context,name):

    try:
        if " HTML " in name[0]: 
            return "doc"
        elif name[0] == "ArcGIS Services":
            return "api"
        else: 
            return "file"
    except:
        return "file"

def clean_keyword(context, keyword):
    try:
        return keyword[0].replace("(", " ").replace(")"," ").replace(u"\u2013"," ").replace(u"\u2019","'")
    except IndexError:
        return ""

def language_from_name(context,s):
    return s[0].split(":")[-1].replace("-","; ")

def strip_whitespace(json_data):
    for key, value in get_items(json_data):
       print key
       if hasattr(value, 'strip'): #we have json string
           json_data[key]=value.strip()
       else:
           strip_whitespace(value)

def polygon(context, points):
    
    points = points[0].split(", ")
    extent_template = Template('''{"type": "Polygon", "coordinates": [[[$minx, $miny], [$minx, $maxy], [$maxx, $maxy], [$maxx, $miny], [$minx, $miny]]]}''')
    return extent_template.substitute(
                                minx = points[0],
                                miny = points[1],
                                maxx = points[2],
                                maxy = points[3]

                                )
def make_notes(context,c1,c2):
    try:
        # check for existance
        foo = (c1[0],c2[0])
    except:
        return c1[0]
    new = " ".join([n.lstrip(":").replace("\n","").replace(":htt",": htt") for n in c2[0].split("\n:")])
    return c1[0] + "\n"+ new
    
def clean_keywords(s): 
    return ",".join(set([n.strip().replace("/"," ") for n in s.split(",") if n.strip()]))
   
def nap_reduce(file,transform):
    class FileResolver(etree.Resolver):
        def resolve(self, url, pubid, context):
            return self.resolve_filename(url, context)
            
    #prefixmap = {'f':'http://www.jakobsen.ca/myfunctions'}
    parser = etree.XMLParser()
    ns = etree.FunctionNamespace('http://data.gc.ca/functions')
    ns['polygon'] = polygon
    ns['format_from_url'] = format_from_url
    ns['size_from_name'] = size_from_name
    ns['language_from_name'] = language_from_name
    ns['resource_name_from_name']=resource_name_from_name
    ns['resource_type_from_name']=resource_type_from_name
    ns['update_frequency']=update_frequency
    ns['make_notes']=make_notes
    ns['check_date']=check_date
    ns['clean_keyword']=clean_keyword
    ns.prefix = 'od'
    parser.resolvers.add(FileResolver())
    xml_input = etree.parse(open(file,'r'), parser)
    xslt_root = etree.parse(open(transform,'r'), parser)
    transform = etree.XSLT(xslt_root)
    
    # Get the node tree that results from the transformation
    result = transform(xml_input)
    package = result.getroot()
    pack={}
    for f in package.getchildren():
        if f.tag!='resources':
            pack[f.tag]=f.text.strip()if f.text else ""
        
    #print str(result)
    resources =  result.find('resources')
    
    res=[]
    for r in resources.getchildren():
        resource={}
        for e in r.getchildren():
            resource[e.tag]=e.text
            #if e.tag=='language':resource[e.tag]=extract_language_from_name(e.text)
        res.append(resource)
    pack['resources']=res
    pack['keywords'] = clean_keywords(pack['keywords'])
    pack['keywords_fra'] =   clean_keywords(pack['keywords_fra'])
    pack['ready_to_publish']=False
    print pack['date_published']
    #print json.dumps(pack,sort_keys=True,indent=4, separators=(',', ': '))
    return json.dumps(pack)

    
def process(dir,outfile): 
    transform = 'iso19139.xsl'
    jlfile = open(os.path.normpath(outfile), "w")
    for (path, dirs, files) in os.walk(os.path.normpath(dir)):
        for file in files:
            if file =='metadata.iso19139.xml':
                jlfile.write(nap_reduce(os.path.join(path,file),transform)+"\n")
    jlfile.close()
if __name__ == '__main__':
   file = "iso19139.xml"
   outfile =helpers.load_dir()+"ec.jl"
   dir="/Users/peder/dev/OpenData/data_sources/ec/"

   process(dir,outfile)
   #transform='json.xsl'
   
  
