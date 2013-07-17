===============
CKAN Data Tools
===============

Author: Peder Jakobsen
:Date: July 16, 2013

.. contents::

Summary
=======

A command line interface that provides access to a number of tools and services related to the Government of Canada Open Data project:

* Transformation of various GoC dataset formats
* Import data from existing GoC datasets
* Purge partial data from existing CKAN instances
* Move and update partial datasets between CKAN instances
* Test datasets and generate reports
* Facilities for working with JSON data using test proxies such as Charles

Example Use
===========

Nested command structure is as follows:

$python munge.py <DATAPOINT> <COMMAND> <ENTITY> <OWNER>

For example, to delete all packages for Agriculture:

$python munge.py ckan delete pack agriculture

Complete documentation can be obtained with $python munge.py -h

Create Organizations:

(my_virtual_env) $python datatools.py ckan init org -s=http://data.statcan.gc.ca/data -k=yourapikey -p=http://127.0.0.1:8888

Load data from a CKAN .jl file:

File must contain valid ckan 2.0 packages.

(my_virtual_env) $python datatools.py ckan load pack -s=http://data.statcan.gc.ca/data -k=yourkey -p=http://proxyuser:proxypass@stcweb.statcan.ca:80 -j=c:\temp\pilot-complete.jl

Reporting
=========

Find out how many packages are in various CKAN servers:

$python datatools.py ckan report pack -s=http://data.gov.uk

Sometimes the most effective way to find data is to interact directly with the .jl load files using grep. 

For example, if you wish to ask "How many pilot files are from statcan?":

grep -c  '"owner_org": "statcan"'  pilot.jl


