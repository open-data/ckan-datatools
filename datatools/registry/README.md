Rules for publishing workflow
==========

If a record is pending, it should have ready_to_publish=True and no portal_release_date=null
The default portal_release_date should be June 18, date of launc

cleanup.py
==========

This module is used to delete files from registry.statcan.gc.ca. It uses *.delete files from ckan_datatools/data/deletes

changes so far:
--------------
1. Deletes:
cansim -
french_ids -
june18_duplicates 
old_geo_ids
pre_launch

2: Additions:

3. h. 



>>>>>>>>>> Library of Pariament record in day 2013-06-?






get_touched.py
==============

Performs analysis on the registry to find what users have worked on what files.  It downloads the json packages for any files 
that are new or have been changed since being loaded in a .jl file.  This file is saved to the data directory as touched_in_registry.jl

report.py
=========

For analyzing changes in the touched_on_registry.jl file compared with .jl load files in order to determine how to best update the data 
on the data without overwriting important fields.

So far, the analysis has revealed the following:

ready_to_publish and portal_release_date are missing from many registry files as of June 20.  
The portal_release_data should be added to all new files and set to some date in the past.


Solution:  create a new .jl load file with the 152 changed records, and add these files. 
Also, create a .jl file for new records that should be transferred from registry to public, or will Ian's script handle this?

Add data_series_identification to AAFC-AIMIS-RP-2614 for all records from aafc-aac