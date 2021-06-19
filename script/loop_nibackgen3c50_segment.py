#!/usr/bin/env python

import os 

#for line in open('input/obsidlst/BKGD_RXTE_1_test.lst'):
for i in [1,2,3,4,5,6,8]:
	for line in open('input/obsidlst/BKGD_RXTE_%d.lst' % i):
		cols = line.split()
		obsid = cols[1]
		print(obsid)

		cmd = 'nibackgenml/preprocessing.py %s' % obsid
		print(cmd);os.system(cmd)

		cmd = 'nibackgenml/nibackgen3c50_obsid.py %s' % obsid
		print(cmd);os.system(cmd)

		cmd = 'nibackgenml/nibackgen3c50_segment.py %s 100.0 10' % obsid
		print(cmd);os.system(cmd)

