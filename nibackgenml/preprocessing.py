#!/usr/bin/env python

import os 
import glob
import argparse
import astropy.io.fits as fits

__author__ = 'Teruaki Enoto'
__version__ = '0.01' # 2021-06-02

#nicerl2_gcalfile = '/Users/enoto/work/soft/heasoft/nicer/nibackgen3c50/develop/202007_RGv6/nixtiflightpi20170601v003_optmv10.fits'

def get_parser():
	"""
	Creates a new argument parser.
	"""
	parser = argparse.ArgumentParser('preprocessing.py',
		formatter_class=argparse.RawDescriptionHelpFormatter,
		description="""
Run a piepline for one NICER ObsID data. 
		"""
		)
	version = '%(prog)s ' + __version__
	parser.add_argument('obsid', type=str, 
		help='ObsID (e.g., 4012010109)')	
	return parser

def copy_data(obsid):
	tmp = glob.glob('%s/*/%s' % (os.getenv('NIBACKGENML_HEASARC_NICERDIR'),obsid))
	if len(tmp) == 0:
		print("Error: no target obsid directory:%s" % obsid)
		return -1
	obsid_path_original = tmp[0]
	print("target original directory: %s" % obsid_path_original)		

	clevt = '%s/xti/event_cl/ni%s_0mpu7_cl.evt.gz' % (obsid_path_original,obsid)
	if not os.path.exists(clevt):
		print("Error: No input clevt file.")
		return -1
	hdu = fits.open(clevt)
	keyword_object = hdu[1].header['OBJECT']
	print(keyword_object)

	path_target_dir = '%s/%s' % (os.getenv('NIBACKGENML_PRODUCT_DIR'),keyword_object)
	if not os.path.exists(path_target_dir):
		cmd = 'mkdir -p %s' % path_target_dir
		print(cmd);os.system(cmd)

	obsid_path_target = '%s/%s' % (path_target_dir,obsid)
	if os.path.exists(obsid_path_target):
		print("Skip: output file has already existed, %s" % obsid_path_target)
		return -1 
	else:
		cmd = 'cp -r %s %s' % (obsid_path_original,obsid_path_target)
		print(cmd);os.system(cmd)
		return obsid_path_target 

def run_niprefilter2(obsid,obsid_path_target):
	cmd  = 'niprefilter2 indir=%s ' % obsid_path_target
	cmd += 'infile=%s/auxil/ni%s.mkf outfile=INFILE clobber=YES ' % (obsid_path_target,obsid)
	cmd += 'coltypes="base,3c50" '
	print(cmd);os.system(cmd)

def run_nicerl2(obsid,obsid_path_target):
	# prepare a script for nicerl2 for each ObsID
	fcmd_nicerl2 = '%s/nicerl2_%s.sh' % (obsid_path_target,obsid)
	flog_nicerl2 = '%s/nicerl2_%s.log' % (obsid_path_target,obsid)
	f = open(fcmd_nicerl2,'w')
	dump  = '#!/bin/sh -f\n'
	dump += 'nicerl2 indir=%s ' % (obsid_path_target)
	dump += 'picalfile=%s ' % os.getenv('NIBACKGENML_NICERL2_GCALFILE')
	dump += 'clobber=yes '
	dump += '> %s 2>&1 ' % flog_nicerl2
	dump += '\n'
	f.write(dump)
	f.close()

	# run the script.
	cmd  = 'chmod +x %s\n' % fcmd_nicerl2
	cmd += '%s' % fcmd_nicerl2
	print(cmd)
	os.system(cmd)

def main(args=None):
	parser = get_parser()
	args = parser.parse_args(args)

	print("ObsID: %s" % args.obsid)
	obsid_path_target = copy_data(args.obsid)
	if obsid_path_target == -1:
		print("skip: %s" % args.obsid)
		exit()
	run_niprefilter2(args.obsid,obsid_path_target)
	run_nicerl2(args.obsid,obsid_path_target)

if __name__=="__main__":
	main()