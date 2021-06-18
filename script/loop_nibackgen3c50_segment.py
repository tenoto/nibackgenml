#!/usr/bin/env python

import os 

for line in open('input/obsidlst/BKGD_RXTE_1.lst'):
	cols = line.split()
	obsid = cols[1]
	print(obsid)

	cmd = 'nibackgenml/preprocessing.py %s' % obsid
	print(cmd);os.system(cmd)

	cmd = 'nibackgenml/nibackgen3c50_obsid.py %s' % obsid
	print(cmd);os.system(cmd)
	
	cmd = 'nibackgenml/nibackgen3c50_segment.py %s 100.0 10' % obsid
	print(cmd);os.system(cmd)

