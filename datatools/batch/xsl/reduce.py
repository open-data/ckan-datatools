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
              'http://maps-cartes.ec.gc.ca/ArcGIS/rest/services/CESI_AirEmissions_NOx/MapServer':"api",
              'TableView.aspx?':'html'
              
              }

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
    print name
    try:
        size=''
        name = name[0]
        print name

        if  " Kb)" in name:
            size = name.split(' Kb)')[0].split(" - ")[1].strip()
        elif " Ko)" in name:
            size =name.split(' Ko)')[0].split(" - ")[1].strip()
        elif " B)" in name:
           size =name.split(' B)')[0].split(" - ")[1].strip()
        elif " O)" in name:
            size =name.split(' O)')[0].split(" - ")[1].strip()
        else:
            return ""
        return size
    except:
        raise
        return "888"
    
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
        else: 
            return "file"
    except:
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

def clean_keywords(s): 
    return ",".join(set([n.strip() for n in s.split(",") if n.strip()]))
     
def nap_reduce(file,transform):
    print file
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
            pack[f.tag]=f.text.strip() if f.text else ""
        
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
    print json.dumps(pack['resources'],sort_keys=True,indent=4, separators=(',', ': '))

    
def process(dir,outfile): 
    transform = 'iso19139.xsl'
    counter=0
    #jlfile = open(os.path.normpath(outfile), "w")
    for (path, dirs, files) in os.walk(os.path.normpath(dir)):
        for file in files:
            if file =='metadata.iso19139.xml':
                counter+=1
                nap_reduce(os.path.join(path,file),transform)
                
if __name__ == '__main__':
   file = "iso19139.xml"
   outfile =helpers.load_dir()+"ec.jl"
   dir="/Users/peder/dev/OpenData/data_sources/ec/"

   process(dir,outfile)
   #transform='json.xsl'
   
  
