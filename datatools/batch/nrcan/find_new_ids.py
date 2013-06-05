import os

def get_ids(dir): 
    ids=[]
    for (path, dirs, files) in os.walk(os.path.normpath(dir)):
        for n,file in enumerate(files):
            id = file.split(".")[0]

            ids.append(id)
            #if (n % 100) == 0: print n 
    return ids


if __name__ == "__main__":
    new_dir="/Users/peder/dev/OpenData/nrcandump"
    old_dir="/Users/peder/dev/goc/nap/en"
    new=get_ids(new_dir)
    old=get_ids(old_dir)
#    print len(old), len(new)
#    print "Intersection", len(set(new).intersection(set(old)))
#
#    print "Symmetric Difference", set(new).symmetric_difference(set(old))
#    print "Files that exist in new, but not in old", len(set(new).difference(set(old)))
    diff = set(old).difference(set(new))
#    print "Files that exist in old, but not in new", len(diff)
    for id in list(diff):
        print id
    
    
    
