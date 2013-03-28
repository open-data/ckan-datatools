File Format Guide
=================

NRCAN
-----

.nap files contain North American Profile of ISO 19115

http://www.fgdc.gov/standards/projects/incits-l1-standards-projects/NAP-Metadata

List of file formats in schema

CSV, GeoTIFF, KML / KMZ, RDF, RSS, SHP, XML, DOC, EXE, GeoRSS, GIF, HTML, IATI, JPG, JSON, NetCDF, ODP, ODS, ODT, PDF, PNG, PPT, RDFa, RTF, SAV, SQL, TXT, XLS, XLSM, Zip, 

TOTAL  FILES  170176

|All Geogratis Formats        |   Number   |
|:-------------|-----------:|
|gzip (GNU zip)|2828|
|ESRI Shapefile|1196|
|Adobe PDF|13748|
|SEGY|603|
|ZIP|3679|
|JPEG 2000|775|
|EDI|1816|
|PDF - Portable Document Format|2215|
|JPEG|513|
|Hierarchical Data Format (HDF)|1003|
|TIFF (Tag Image File Format)|13034|
|GeoTIFF|38232|
|Shape|12502|
|GeoTIFF (Georeferenced Tag Image File Format)|39774|
|GML (Geography Markup Language)|14463|
|ASCII (American Standard Code for Information Interchange)|9127|
|CDED ASCII|14579|
|CorelDraw|89|


----------

|Known Schema Formats        |   Number   |
|:-------------|-----------:|
|GeoTIFF|163995|
|Adobe PDF|61837|
|GeoTIFF (Georeferenced Tag Image File Format)|227950|
|PDF - Portable Document Format|24365|

-------------------


|Uknown Geogratis Formats        |   Number   |
|:-------------|-----------:|
|gzip (GNU zip)|5597|
|ESRI Shapefile|1196|
|SEGY|1988|
|ZIP|5512|
|JPEG 2000|4650|
|EDI|2139|
|JPEG|1344|
|Hierarchical Data Format (HDF)|10123|
|TIFF (Tag Image File Format)|91238|
|Shape|87514|
|GML (Geography Markup Language)|101241|
|ASCII (American Standard Code for Information Interchange)|45635|
|CDED ASCII|72895|
|CorelDraw|1237|

TOTAL  1080632
### Entity Guide  ###

6.3.7. Keywords
Type: MD_Keywords
Description: Commonly used words or phases which describe the resource. 
Optionally, the keyword type and a citation for the authoritative or 
registered resource of the keywords are also provided.
BP: The use of keywords from authoritative source instead of using user defined keywords is highly recommended or communities should develop specific 
thesaurus of keywords and make them available on the Web for its use with this profile.

//gmd:MD_KeywordTypeCode[@codeListValue="%s"]/../../gmd:keyword/gco:CharacterString

