''' Reducing complex XML files to something more simple '''
from lxml import etree
import sys
import lxml
from lxml import objectify
import simplejson as json
from pprint import pprint
from string import Template
import xmltodict as xmltodict
from collections import OrderedDict
from pkgutil import  simplegeneric


class objectJSONEncoder(json.JSONEncoder):
    """A specialized JSON encoder that can handle simple lxml objectify types
       >>> from lxml import objectify
       >>> obj = objectify.fromstring("<Book><price>1.50</price><author>W. Shakespeare</author></Book>")
       >>> objectJSONEncoder().encode(obj)
       '{"price": 1.5, "author": "W. Shakespeare"}'       
    """
    def default(self,o):
        if isinstance(o, lxml.objectify.IntElement):
            return int(o)
        if isinstance(o, lxml.objectify.NumberElement) or isinstance(o, lxml.objectify.FloatElement):
            return float(o)
        if isinstance(o, lxml.objectify.ObjectifiedDataElement):
            return str(o)
        if hasattr(o, '__dict__'):
            #For objects with a __dict__, return the encoding of the __dict__
            return o.__dict__
        return json.JSONEncoder.default(self, o)


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
    class FileResolver(etree.Resolver):
        def resolve(self, url, pubid, context):
            return self.resolve_filename(url, context)



    #prefixmap = {'f':'http://www.jakobsen.ca/myfunctions'}
    parser = etree.XMLParser()
    ns = etree.FunctionNamespace('http://www.jakobsen.ca/myfunctions')
    ns['polygon'] = polygon
    ns.prefix = 'pj'
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
        res.append(resource)
    pack['resources']=res
    pack['keywords'] = clean_keywords(pack['keywords'])
    pack['keywords_fra'] =   clean_keywords(pack['keywords_fra'])
    pprint(pack)
   


if __name__ == '__main__':
   file = "iso19139.xml"
   transform = 'iso19139.xsl'
   #transform='json.xsl'
   nap_reduce(file,transform)
