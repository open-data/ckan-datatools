#!/usr/bin/python
import subprocess

subprocess.checkcall("ls", shell=True)


subprocess.call("'/temp/postgresql/9.1.4/contrib/postgis-1.5')"
 
# fetch, compile and install PostGIS
wget http://postgis.refractions.net/download/postgis-1.5.3.tar.gz
tar zxvf postgis-1.5.3.tar.gz && cd postgis-1.5.3/
sudo ./configure && sudo make && sudo checkinstall --pkgname postgis-1.5.3 --pkgversion 1.5.3-src --default

# now create the template_postgis database template
#sudo su postgres -c'createdb -E UTF8 -U postgres template_postgis'
#sudo su postgres -c'createlang -d template_postgis plpgsql;'
sudo -c'psql -d ckantest7 -c"CREATE EXTENSION hstore;"'
sudo -c'psql -d ckantest7 -f /usr/share/postgresql/9.1/contrib/postgis-1.5/postgis.sql'
sudo -c'ppsql -d ckantest7  -f /usr/share/postgresql/9.1/contrib/postgis-1.5/spatial_ref_sys.sql'
sudo -c'psql -d ckantest7 -c"select postgis_lib_version();"'
sudo -c'psql -d ckantest7 -c "GRANT ALL ON geometry_columns TO PUBLIC;"'
sudo -c'psql -d ckantest7 -c "GRANT ALL ON spatial_ref_sys TO PUBLIC;"'
sudo -c'psql -d ckantest7 -c "GRANT ALL ON geography_columns TO PUBLIC;"'
echo "Done!"

#Create variables out of shell commands
MESSAGES = "tail /var/log/messages"
SPACE = "df -h"

#Places variables into a list/array
cmds = [MESSAGES, SPACE]

#Create a function, that takes a list parameter
#Function uses default keyword parameter of cmds
def runCommands(commands=cmds):
    #Iterates over list, running statements for each item in the list
    count=0
    for cmd in cmds:
        count+=1
        print "Running Command Number %s" % count
        subprocess.call(cmd, shell=True)

#Function is called
runCommands()