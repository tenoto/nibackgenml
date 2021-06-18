#!/usr/bin/env python

import os 
import glob
import pandas as pd
import argparse
import astropy.io.fits as fits

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
	parser.add_argument('obsid',type=str,help='ObsID (e.g., 4012010109)')	
	parser.add_argument('timebin',type=float,help='Time bin (sec)')		
	parser.add_argument('timegap',type=float,help='Gap time (sec) to be connected to a single segment')			
	return parser

def generate_segment_table(obsid,timebin,timegap):
	print("ObsID: %s" % obsid)
	print("Timebin: %s" % timebin)	

	target = glob.glob("%s/*/%s" % (os.getenv('NIBACKGENML_PRODUCT_DIR'),obsid))
	if len(target) == 0:
		print("no %s directory." % obsid)
		return -1 
	obsid_path_target = target[0]

	outdir = '%s/bkg_segment' % obsid_path_target
	cmd = 'rm -rf %s; mkdir -p %s' % (outdir,outdir)
	print(cmd);os.system(cmd)

	clevt = '%s/xti/event_cl/ni%s_0mpu7_cl.evt' % (obsid_path_target,obsid)
	hdu = fits.open(clevt)
	gti = hdu['GTI'].data
	number_of_gti = len(gti)

	#########################
	# Check GTI parameters
	#########################	
	file_gti_all = '%s/ni%s_gti.lst' % (outdir,obsid)
	f_gti_all = open(file_gti_all,'w')
	dump = 'gti,seg,start,stop,exp,sumexp,diff\n'
	f_gti_all.write(dump)
	gti_segment_lst = []
	current_segment_id = 0
	gti_expsum_lst = []
	tmp_expsum = 0
	for i in range(number_of_gti):
		if i == 0: # first 
			gap_to_previous = 0
		else:
			gap_to_previous = gti['START'][i] - gti['STOP'][i-1]
		gtiexp = gti['STOP'][i] - gti['START'][i]

		if gap_to_previous > timegap:
			current_segment_id += 1 
			tmp_expsum = gtiexp
			gti_expsum_lst.append(tmp_expsum)			
		else:
			tmp_expsum += gtiexp
			gti_expsum_lst.append(tmp_expsum)
		dump = '%d,%d,%.1f,%.1f,%.1f,%.1f,%1f\n' % (i,current_segment_id,gti['START'][i],gti['STOP'][i],gtiexp,tmp_expsum,gap_to_previous)
		#print(dump)
		f_gti_all.write(dump)
	f_gti_all.close()

	############################
	# Combine GTIs to Segements
	############################
	df_gti_all = pd.read_csv(file_gti_all,
		dtype={'seg':int})
	#print(df_gti_all)

	file_segment_sorted = '%s/ni%s_segment.lst' % (outdir,obsid)
	f_segment_sorted = open(file_segment_sorted,'w')
	dump = 'seg,start,stop,duration,exp\n'
	f_segment_sorted.write(dump)

	number_of_segments = int(df_gti_all.tail(1)['seg']) + 1
	for segnum in range(number_of_segments):
		flag = (df_gti_all['seg'] == segnum)
		seg_start = float(df_gti_all[flag].head(1)['start'])
		seg_stop = float(df_gti_all[flag].tail(1)['stop'])
		seg_sumexp = float(df_gti_all[flag].tail(1)['sumexp'])		
		seg_duration = seg_stop - seg_start
		dump = '%d,%.1f,%.1f,%.1f,%.1f\n' % (segnum,seg_start,seg_stop,seg_duration,seg_sumexp)
		f_segment_sorted.write(dump)
	f_segment_sorted.close()	

	############################
	# Divide Segments to Blocks
	############################
	file_block_sorted = '%s/ni%s_block.lst' % (outdir,obsid)
	f_block_sorted = open(file_block_sorted,'w')
	dump = 'gti,seg,block,start,stop,duration,exp\n'
	f_block_sorted.write(dump)

	print(df_gti_all)

	block_num = 0 		
	for segnum in range(number_of_segments):
		flag = (df_gti_all['seg'] == segnum)
		seg_start = float(df_gti_all[flag].head(1)['start'])
		seg_stop = float(df_gti_all[flag].tail(1)['stop'])
		seg_sumexp = float(df_gti_all[flag].tail(1)['sumexp'])		
		seg_duration = seg_stop - seg_start
		dump = '%d,%.1f,%.1f,%.1f,%.1f\n' % (segnum,seg_start,seg_stop,seg_duration,seg_sumexp)

		if seg_sumexp < timebin:
			continue

		block_exp = 0
		block_tstart = float(df_gti_all[flag].head(1)['start'])
		block_tstop = block_tstart
		for index, row in df_gti_all[flag].iterrows():
			print(int(row['gti']),int(row['seg']),row['start'],row['stop'],row['exp'])			
			if block_exp + float(row['exp']) >= timebin:
				#print(int(row['gti']),int(row['seg']),float(row['start']),float(row['stop']))
				block_tstop = float(row['start']) + timebin - block_exp
				block_exp += block_tstop - float(row['start'])
				block_duration = block_tstop - block_tstart
				dump = '%d,%d,%d,' % (row['gti'],row['seg'],block_num)
				dump += '%.1f,%.1f,%.1f,%.1f' % (block_tstart,block_tstop,block_duration,block_exp)
				dump += '\n'
				print(dump)
				f_block_sorted.write(dump)
				# initialization 
				block_exp = 0.0
				block_tstart = block_tstop
				block_tstop = block_tstop
				block_num += 1 
			else:
				block_exp += float(row['exp'])
	f_block_sorted.close()

def run_nibackgen3c50_segment(obsid,dtmin=10.0,dtmax=50.0):

	target = glob.glob("%s/*/%s" % (os.getenv('NIBACKGENML_PRODUCT_DIR'),obsid))
	if len(target) == 0:
		print("no %s directory." % obsid)
		return -1 
	obsid_path_target = target[0]

	outdir = '%s/bkg_segment' % obsid_path_target
	file_block_sorted = '%s/ni%s_block.lst' % (outdir,obsid)

	df_block_sorted = pd.read_csv(file_block_sorted,
		dtype={'gti':int,'seg':int,'block':int})
	print(df_block_sorted)

	clevt = '%s/xti/event_cl/ni%s_0mpu7_cl.evt' % (obsid_path_target,obsid)
	ufaevt = "%s/xti/event_cl/ni%s_0mpu7_ufa.evt" % (obsid_path_target,obsid)		

	for index, row in df_block_sorted.iterrows():
		block_num = int(row['block'])

		suboutdir = '%s/block%03d' % (outdir,block_num)
		cmd = 'rm -rf %s;mkdir -p %s;' % (suboutdir,suboutdir)
		print(cmd);os.system(cmd)

		cmd = 'rm -f xsel*'
		print(cmd);os.system(cmd)

		tstart = float(row['start'])
		tstop = float(row['stop'])
	
		filtered_clevt = '%s/ni%s_block%03d_0mpu7_cl.evt' % (suboutdir,obsid,block_num)
		filtered_ufaevt = '%s/ni%s_block%03d_0mpu7_ufa.evt' % (suboutdir,obsid,block_num)		

		cmd  = "xselect << EOF\n"
		cmd += "xsel\n"
		cmd += "read event %s\n" % clevt 
		cmd += "/\n"
		cmd += "yes\n"
		cmd += "filter time scc\n"
		cmd += "%.1f,%.1f\n" % (tstart,tstop)
		cmd += "x\n" 
		cmd += "extract event\n"
		cmd += "save event\n"
		cmd += "%s\n" % filtered_clevt
		cmd += "yes\n"
		cmd += "exit\n"
		cmd += "no\n"
		cmd += "EOF\n"
		print(cmd);os.system(cmd)

		cmd = 'rm -f xsel*'
		print(cmd);os.system(cmd)	

		cmd  = "xselect << EOF\n"
		cmd += "xsel\n"
		cmd += "read event %s\n" % ufaevt 
		cmd += "/\n"
		cmd += "yes\n"
		cmd += "filter time scc\n"
		cmd += "%.1f,%.1f\n" % (tstart,tstop)
		cmd += "x\n" 
		cmd += "extract event\n"
		cmd += "save event\n"
		cmd += "%s\n" % filtered_ufaevt
		cmd += "yes\n"
		cmd += "exit\n"
		cmd += "no\n"
		cmd += "EOF\n"
		print(cmd);os.system(cmd)

		cmd = 'rm -f xsel*'
		print(cmd);os.system(cmd)		


		totspec = 'ni%s_block%03d_3c50_tot' % (obsid,block_num)
		bkgspec = 'ni%s_block%03d_3c50_bkg' % (obsid,block_num)						

		fscript_file = '%s/ni%s_block%03d_nibackgen3c50.sh' % (suboutdir,obsid,block_num)
		fscript_log = '%s/ni%s_block%03d_nibackgen3c50.log' % (suboutdir,obsid,block_num)
		fscript = open(fscript_file,'w')
		dump  = '#!/bin/sh -f \n'
		dump += 'nibackgen3C50 ' 
		dump += 'rootdir="NONE" '
		dump += 'obsid="NONE" ' 
		dump += 'bkgidxdir="%s" ' % os.getenv("NIBACKGEN3C50_BKGIDXDIR")
		dump += 'bkglibdir="%s" ' % os.getenv("NIBACKGEN3C50_BKGIDXDIR")
		dump += 'gainepoch="%s" ' % os.getenv("NIBACKGEN3C50_GAINEPOCH")
		dump += 'calevtdir="NONE" '
		dump += 'ufafile="%s" ' % filtered_ufaevt
		dump += 'clfile="%s" ' % filtered_clevt
		dump += 'dtmin=%d ' % dtmin 
		dump += 'dtmax=%d ' % dtmax
		dump += 'totspec=%s ' % totspec
		dump += 'bkgspec=%s ' % bkgspec
		dump += '>& %s' % fscript_log
		fscript.write(dump)
		fscript.close()
		cmd = 'chmod +x %s' % fscript_file
		print(cmd);os.system(cmd)
		cmd = '%s' % fscript_file
		print(cmd);os.system(cmd)
		
		cmd = 'mv ni%s_block%03d_3c50_*.pi %s' % (obsid,block_num,suboutdir)
		print(cmd);os.system(cmd)

		outfig_basename = 'ni%s_block%03d_3c50_sub' % (obsid,block_num)

		cmd = 'xspec << EOF\n'
		cmd += 'data 1 %s/%s.pi\n' % (suboutdir,totspec)
		cmd += 'back 1 %s/%s.pi\n' % (suboutdir,bkgspec)		
		cmd += 'resp 1 input/resp/nixti20170601_combined_v002_xti50_wo14_34.rmf\n'
		cmd += 'arf 1 input/resp/nixtionaxis20170601_combined_v004_xti50_wo14_34.arf\n'
		cmd += 'setplot energy\n'
		cmd += 'ignore **-0.2,12.0-**\n'
		cmd += 'iplot d\n'
		cmd += 'hard %s.ps/cps\n' % outfig_basename
		cmd += 'exit\n'
		cmd += 'exit\n'
		print(cmd);os.system(cmd)

		cmd = 'ps2pdf %s.ps; rm -f %s.ps;' % (outfig_basename,outfig_basename)
		cmd += 'mv %s.pdf %s' % (outfig_basename,suboutdir)
		print(cmd);os.system(cmd)


def main(args=None):
	parser = get_parser()
	args = parser.parse_args(args)

	generate_segment_table(args.obsid,args.timebin,args.timegap)
	run_nibackgen3c50_segment(args.obsid)

if __name__=="__main__":
	main()