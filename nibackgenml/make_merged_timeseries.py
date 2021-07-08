#!/usr/bin/env python

import os 
import glob
import argparse
import numpy as np 
import pandas as pd
import astropy.io.fits as fits

__author__ = 'Teruaki Enoto'
__version__ = '0.01' # 2021-07-08

sample_bands = [[0,25],[35,200],[200,800],[800,1200],[1200,1500],[1500,1700]]
# https://heasarc.gsfc.nasa.gov/lheasoft/ftools/headas/nicerpi.html

mkf_select_column_dict = {
	"RA":["deg","D"],
	"DEC":["deg","D"],	
	"ROLL":["deg","D"],	
	"SAT_LAT":["deg","D"],
	"SAT_LON":["deg","D"],	
	"SAT_ALT":["km","D"],
	"ELV":["deg","D"],
	"BR_EARTH":["deg","D"],
	"SUNSHINE":["","I"],		
	"SUN_ANGLE":["deg","D"],
	"LOCAL_TIME":["deg","D"],
	"MOON_ANGLE":["deg","D"],
	"RAM_ANGLE":["deg","D"],
	"EAST_ANGLE":["deg","D"],
	"ANG_DIST":["deg","D"],
	"SAA":["","I"],
	"SAA_TIME":["s","D"],
	"COR_ASCA":["GeV/c","D"],
	"COR_SAX":["GeV/c","D"],
	"MCILWAIN_L":["","I"],
	"MAGFIELD":["G","D"],
	"MAGFIELD_MIN":["G","D"],
	"MAG_ANGLE":["deg","D"],
	"SUN_RA":["deg","D"],		
	"SUN_DEC":["deg","D"],
	"MOON_RA":["deg","D"],
	"MOON_DEC":["deg","D"],
	"EARTH_RA":["deg","D"],	
	"EARTH_DEC":["deg","D"],
	"ATT_ANG_AZ":["deg","D"],
	"ATT_ANG_EL":["deg","D"],		
	"ATT_ERR_AZ":["deg","D"],
	"ATT_ERR_EL":["deg","D"],
	"TOT_ALL_COUNT":["","I"],
	"TOT_UNDER_COUNT":["","I"],	
	"TOT_OVER_COUNT":["","I"],
	"TOT_XRAY_COUNT":["","I"],
	"NUM_FPM_ON":["","I"],
	"FPM_RATIO_REJ_COUNT":["","D"],
	"FPM_XRAY_PI_0000_0025":["","D"],
	"FPM_XRAY_PI_0035_0200":["","D"],
	"FPM_XRAY_PI_0200_0800":["","D"],
	"FPM_XRAY_PI_0800_1200":["","D"],
	"FPM_XRAY_PI_1200_1500":["","D"],
	"FPM_XRAY_PI_1500_1700":["","D"],
	"FPM_XRAY_PI_COUNT":["","D"],
	"FPM_DOUBLE_COUNT":["","D"],
	"FPM_OVERONLY_COUNT":["","D"],
	"FPM_UNDERONLY_COUNT":["","D"],
	"FPM_FT_COUNT":["","D"],	
	"FPM_NOISE25_COUNT":["","D"]											
	}

def get_parser():
	"""
	Creates a new argument parser.
	"""
	parser = argparse.ArgumentParser('make_merged_timeseries.py',
		formatter_class=argparse.RawDescriptionHelpFormatter,
		description="""
Make a single fits file for binned data.
		"""
		)
	version = '%(prog)s ' + __version__
	parser.add_argument('indir',type=str,help='Input directory.')	
	parser.add_argument('outfitsfile',type=str,help='Output fitsfile.')		
	return parser

def get_rate_tot(tot_pha,chmin,chmax):
	hdu = fits.open(tot_pha)
	exposure = hdu['SPECTRUM'].header['EXPOSURE']
	flag = np.logical_and(
		hdu['SPECTRUM'].data['CHANNEL'] >= chmin,
		hdu['SPECTRUM'].data['CHANNEL'] < chmax)
	count = sum(hdu['SPECTRUM'].data['COUNTS'][flag])
	rate = float(count) / exposure 
	rate_error = np.sqrt(float(count)) / exposure 
	return rate,rate_error

def get_rate_bkg(bkg_pha,chmin,chmax):
	hdu = fits.open(bkg_pha)
	exposure = hdu['SPECTRUM'].header['EXPOSURE']
	flag = np.logical_and(
		hdu['SPECTRUM'].data['CHANNEL'] >= chmin,
		hdu['SPECTRUM'].data['CHANNEL'] < chmax)
	count = sum(hdu['SPECTRUM'].data['RATE'][flag]*exposure)
	rate = count/exposure
	rate_error = np.sqrt(count)/exposure
	return rate,rate_error

class MergeTable():
	def __init__(self):
		self.obsid = np.array([])		
		self.block_num = np.array([])
		self.tstart = np.array([])		
		self.tstop = np.array([])
		self.exp = np.array([])

		self.tot_rate = [np.array([]) for i in range(len(sample_bands))]
		self.tot_rate_error = [np.array([]) for i in range(len(sample_bands))]

		self.bkg_rate = [np.array([]) for i in range(len(sample_bands))]
		self.bkg_rate_error = [np.array([]) for i in range(len(sample_bands))]		

		self.mkf_keyword = []
		for keyword, value in mkf_select_column_dict.items():
			setattr(self, "%s_MEAN" % keyword, np.array([]))
			setattr(self, "%s_MEDIAN" % keyword, np.array([]))						
			self.mkf_keyword.append(keyword)

def extract_3c50_parameter(block_path,table):
	#print(block_path)

	block_path_subdir_list = block_path.split('/')
	block_num = int(block_path_subdir_list[-1].split('block')[-1])
	obsid = block_path_subdir_list[-3]

	table.obsid = np.append(table.obsid,[obsid])
	table.block_num = np.append(table.block_num,[block_num])

	# ========
	#dump = '%s,%d,' % (obsid,block_num)

	tmp_src_pha = glob.glob('%s/ni*_block*_3c50_tot.pi' % block_path)
	if len(tmp_src_pha) == 0:
		print("No 3c50 src file")
		return -1
	src_pha = tmp_src_pha[0]
	
	src_hdu = fits.open(src_pha)
	src_tstart = src_hdu['GTI'].data['START'][0]
	src_tstop = src_hdu['GTI'].data['STOP'][-1]	
	src_exp = src_hdu['SPECTRUM'].header['EXPOSURE']

	if src_exp == 0:
		return -1

	table.tstart = np.append(table.tstart,[src_tstart])
	table.tstop = np.append(table.tstop,[src_tstop])
	table.exp = np.append(table.exp,[src_exp])

	# ========
	#dump += '%.1f,%.1f,%.1f,' % (src_exp,src_tstart,src_tstop)

	for i in range(len(sample_bands)):
		ch_min = sample_bands[i][0]
		ch_max = sample_bands[i][1]
		rate,rate_err = get_rate_tot(src_pha,ch_min,ch_max)

		table.tot_rate[i] = np.append(table.tot_rate[i],rate)
		table.tot_rate_error[i] = np.append(table.tot_rate_error[i],rate_err)
		#dump += '%.4e,%.4e,' % (rate,rate_err)

	# ========

	tmp_bkg_pha = glob.glob('%s/ni*_block*_3c50_bkg.pi' % block_path)
	if len(tmp_bkg_pha) == 0:
		print("No 3c50 bkg file")
		return -1
	bkg_pha = tmp_bkg_pha[0]

	for i in range(len(sample_bands)):
		ch_min = sample_bands[i][0]
		ch_max = sample_bands[i][1]
		rate,rate_err = get_rate_bkg(bkg_pha,ch_min,ch_max)

		table.bkg_rate[i] = np.append(table.bkg_rate[i],rate)
		table.bkg_rate_error[i] = np.append(table.bkg_rate_error[i],rate_err)
		#dump += '%.4e,%.4e,' % (rate,rate_err)

	# ========

	mkf = '%s/../../auxil/ni%s.mkf' % (block_path,obsid)
	hdu_mkf = fits.open(mkf)
	
	flag = np.logical_and(
		hdu_mkf['PREFILTER'].data['TIME'] >= src_tstart,
		hdu_mkf['PREFILTER'].data['TIME'] < src_tstop)
	for keyword in table.mkf_keyword:
		vars(table)["%s_MEAN" % keyword] = np.append(vars(table)["%s_MEAN" % keyword],
			[np.mean(hdu_mkf["PREFILTER"].data[keyword][flag])])
		vars(table)["%s_MEDIAN" % keyword] = np.append(vars(table)["%s_MEDIAN" % keyword],
			[np.median(hdu_mkf["PREFILTER"].data[keyword][flag])])

def make_merged_timeseries(indir,output_fitsfile):
	print("-----------")	
	print(indir)
	print(output_fitsfile)
	print("-----------")

	cmd = 'rm -f %s' % output_fitsfile
	print(cmd);os.system(cmd)

	table = MergeTable()

	block_path_list = glob.glob('%s/BKGD_RXTE_?/*/bkg_segment/block*' % indir)
	num_of_data = len(block_path_list)
	i = 0
	for block_path in block_path_list:
		print("%d/%d %s" % (i,num_of_data,block_path))
		extract_3c50_parameter(block_path,table)
		i += 1
#		break 

	column_list = []
	column_list.append(fits.Column(name='OBSID',format='20A', array=table.obsid))
	column_list.append(fits.Column(name='BLOCK',format='I', array=table.block_num))
	column_list.append(fits.Column(name='EXPOSURE',format='D', array=table.exp))	
	column_list.append(fits.Column(name='TSTART',format='D', unit='sec', array=table.tstart))
	column_list.append(fits.Column(name='TSTOP',format='D', unit='sec', array=table.tstop))	
	for i in range(len(sample_bands)):
		chmin = sample_bands[i][0]
		chmax = sample_bands[i][1]
		chstr = '%04d_%04d' % (chmin,chmax)
		column_list.append(fits.Column(name='TOT_RATE_%s' % chstr, format='D', unit='c/s', array=table.tot_rate[i]))		
		column_list.append(fits.Column(name='TOT_RERR_%s' % chstr, format='D', unit='c/s', array=table.tot_rate_error[i]))				
		column_list.append(fits.Column(name='BKG_RATE_%s' % chstr, format='D', unit='c/s', array=table.bkg_rate[i]))		
		column_list.append(fits.Column(name='BKG_RERR_%s' % chstr, format='D', unit='c/s', array=table.bkg_rate_error[i]))						

	for keyword, value in mkf_select_column_dict.items():
		print(keyword,value)
		name = '%s_MEAN' % keyword
		print(name)
		column_list.append(fits.Column(name=name,format='D',unit=value[0],array=vars(table)[name]))
		name = '%s_MEDIAN' % keyword
		print(name)
		column_list.append(fits.Column(name=name,format='D',unit=value[0],array=vars(table)[name]))

	column_defs = fits.ColDefs(column_list)
	hdu = fits.BinTableHDU.from_columns(column_defs,name='TIMESERIES')
	hdu.writeto(output_fitsfile)

def main(args=None):
	parser = get_parser()
	args = parser.parse_args(args)

	make_merged_timeseries(args.indir,args.outfitsfile)

if __name__=="__main__":
	main()