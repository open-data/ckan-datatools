File Format Guide
=================

NRCAN
-----

.nap files contain North American Profile of ISO 19115

http://www.fgdc.gov/standards/projects/incits-l1-standards-projects/NAP-Metadata

### Entity Guide  ###

6.3.7. Keywords
Type: MD_Keywords
Description: Commonly used words or phases which describe the resource. 
Optionally, the keyword type and a citation for the authoritative or 
registered resource of the keywords are also provided.
BP: The use of keywords from authoritative source instead of using user defined keywords is highly recommended or communities should develop specific 
thesaurus of keywords and make them available on the Web for its use with this profile.

//gmd:MD_KeywordTypeCode[@codeListValue="%s"]/../../gmd:keyword/gco:CharacterString