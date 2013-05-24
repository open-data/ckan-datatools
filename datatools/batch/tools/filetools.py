## {{{ http://code.activestate.com/recipes/578095/ (r1)
import os
import sys
import linecache

   
def print_first_last_line(inputfile) :
    'gets the last line of a file without reading the entire file into memory'
    filesize = os.path.getsize(inputfile)
    blocksize = 1024
    dat_file = open(inputfile, 'rb')
    headers = dat_file.readline().strip()
    if filesize > blocksize :
        maxseekpoint = (filesize // blocksize)
        dat_file.seek(maxseekpoint*blocksize)
    elif filesize :
        maxseekpoint = blocksize % filesize
        dat_file.seek(maxseekpoint)    
    lines =  dat_file.readlines() 
    print len(lines)   
    if lines :
        last_line = lines[-1].strip()
    print "first line : ", headers
    print "last line : ", last_line

    # Get any line in the file
    #foo = linecache.getline(inputfile, 4)
    #print foo
    
def remove_lines(filename, number_of_lines):
    lines = 0
    f = open("/temp/LOAD/nrcan-1-stripped3.jl","w")
    for line in open(filename):
        lines += 1
        if lines < number_of_lines:
            pass
        else:
            f.write(line)    

if __name__ == "__main__" :
    remove_lines("/temp/LOAD/nrcan-1.jl",37600)
    if len(sys.argv) >= 2:
        print_first_last_line(sys.argv[1])
    else:
        sys.exit("Usage %s filename" % sys.argv[0])
