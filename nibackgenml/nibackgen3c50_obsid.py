#!/usr/bin/env python

import os 
import glob
import argparse

__author__ = 'Teruaki Enoto'
__version__ = '0.01' # 2021-06-18

#nicerl2_gcalfile = '/Users/enoto/work/soft/heasoft/nicer/nibackgen3c50/develop/202007_RGv6/nixtiflightpi20170601v003_optmv10.fits'

def get_parser():
	"""
	Creates a new argument parser.
	"""
	parser = argparse.ArgumentParser('nibackgen3c50_obsid.py',
		formatter_class=argparse.RawDescriptionHelpFormatter,
		description="""
Run nibackgen3c50 for the specified obsid. 
		"""
		)
	version = '%(prog)s ' + __version__
	parser.add_argument('obsid', type=str, 
		help='ObsID (e.g., 4012010109)')	
	return parser

def run_nibackgen3c50_obsid(obsid):
	target = glob.glob("%s/*/%s" % (os.getenv('NIBACKGENML_PRODUCT_DIR'),obsid))
	if len(target) == 0:
		print("no %s directory." % obsid)
		return -1 
	obsid_path_target = target[0]

	outdir = '%s/bkg_obsid' % obsid_path_target
	cmd = 'rm -rf %s;mkdir -p %s' % (outdir,outdir)
	print(cmd);os.system(cmd)

	totspec = 'ni%s_3c50_tot.pi' % obsid
	bkgspec = 'ni%s_3c50_bkg.pi' % obsid

	fscript_file = '%s/nibackgen3c50.sh' % outdir
	fscript_log = '%s/nibackgen3c50.log' % outdir	
	fscript = open(fscript_file,'w')
	dump  = '#!/bin/sh -f \n'
	dump += 'nibackgen3C50 ' 
	dump += 'rootdir="%s" ' % os.path.dirname(obsid_path_target)
	dump += 'obsid=%s ' % obsid
	dump += 'bkgidxdir="%s" ' % os.getenv("NIBACKGEN3C50_BKGIDXDIR")
	dump += 'bkglibdir="%s" ' % os.getenv("NIBACKGEN3C50_BKGIDXDIR")
	dump += 'gainepoch="%s" ' % os.getenv("NIBACKGEN3C50_GAINEPOCH")
	dump += 'totspec=%s ' % totspec
	dump += 'bkgspec=%s ' % bkgspec
	dump += '>& %s' % fscript_log
	fscript.write(dump)
	fscript.close()
	cmd = 'chmod +x %s' % fscript_file
	print(cmd);os.system(cmd)
	cmd = '%s' % fscript_file
	print(cmd);os.system(cmd)
	cmd = 'mv ni%s_3c50_*.pi %s' % (obsid, outdir)
	print(cmd);os.system(cmd)

def main(args=None):
	parser = get_parser()
	args = parser.parse_args(args)

	print("ObsID: %s" % args.obsid)
	run_nibackgen3c50_obsid(args.obsid)

if __name__=="__main__":
	main()