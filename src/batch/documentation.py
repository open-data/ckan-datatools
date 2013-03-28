# THE 

filecounts = [('gzip (GNU zip)', 2828),
 ('ESRI Shapefile', 1196),
 ('Adobe PDF', 13748),
 ('SEGY', 603),
 ('ZIP', 3679),
 ('JPEG 2000', 775),
 ('EDI', 1816),
 ('PDF - Portable Document Format', 2215),
 ('JPEG', 513),
 ('Hierarchical Data Format (HDF)', 1003),
 ('TIFF (Tag Image File Format)', 13034),
 ('GeoTIFF', 38232),
 ('Shape', 12502),
 ('GeoTIFF (Georeferenced Tag Image File Format)', 39774),
 ('GML (Geography Markup Language)', 14463),
 ('ASCII (American Standard Code for Information Interchange)', 9127),
 ('CDED ASCII', 14579),
 ('CorelDraw', 89)]



if __name__ == "__main__":
    print "|File   |Counts|"
    print "|:------|-----:|"
    for (f,n) in filecounts:
        print "| %s |%s|" % (f,n)
