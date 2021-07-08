#!/usr/bin/env python

OUTDIR = 'local/nibackgenml_3c50process_v210622'

import os 
import glob

def copy_obsid_directory(obsid_path):
	if not os.path.exists(obsid_path):
		print("file %s does not exist." % obsid_path)
		return -1 
	obsid = os.path.basename(obsid_path)
	print(obsid)

	newdir = '%s/%s' % (OUTDIR,obsid_path)
	cmd = 'rm -rf %s; mkdir -p %s;' % (newdir,newdir)
	print(cmd);os.system(cmd)

	newdir_xti = '%s/xti/event_cl' % newdir
	clevt = '%s/xti/event_cl/ni%s_0mpu7_cl.evt' % (obsid_path,obsid)
	ufaevt = '%s/xti/event_cl/ni%s_0mpu7_ufa.evt' % (obsid_path,obsid)	
	cmd = 'mkdir -p %s;' % newdir_xti
	cmd += 'cp %s %s;' % (clevt,newdir_xti)
	cmd += 'cp %s %s' % (ufaevt,newdir_xti)
	print(cmd);os.system(cmd)

	newdir_auxil = '%s/auxil' % newdir
	mkffile = '%s/auxil/ni%s.mkf' % (obsid_path,obsid)
	cmd = 'mkdir -p %s;' % newdir_auxil
	cmd += 'cp %s %s;' % (mkffile,newdir_auxil)
	print(cmd);os.system(cmd)	

	cmd = 'cp -r %s/bkg_* %s' % (obsid_path,newdir)
	print(cmd);os.system(cmd)	

cmd = 'rm -rf %s; mkdir -p %s;' % (OUTDIR,OUTDIR)
print(cmd);os.system(cmd)

for obsid_path in glob.glob('local/BKGD_RXTE_*/*'):
	print(obsid_path)
	copy_obsid_directory(obsid_path)	
#copy_obsid_directory("local/BKGD_RXTE_1/1012010188")	

