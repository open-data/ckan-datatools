#!/usr/bin/python

import sys, getopt

def main(argv):

	try:
		opts, args = getopt.getopt(argv, "hi:o", ["munge=","server="])
	except getopt.GetoptError:
		print 'munge.py -m <test|all> -c <ckan> -p <proxy>'
		sys.exit(2)
	for opt, arg in opts:
		if opt == '-h':
			print 'munge.py -m <test|all> -c <ckan> -p <proxy>'

if __name__ == "__main__":
	main(sys.argv[1:])