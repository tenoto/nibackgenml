# nibackgenml

## directory 
- "nibackgenml": A collection of main scripts
- "input": Input data and parameter files 
	- "input/obsidlst": ObsID list for background regions 
- "local": local directory of the large processed data (not uploaded to the github), output directory of the script
- "script": script to run the procedures. 

## Setup and example
%> source nibackgenml/setenv/setenv.bashrc
	- This setup the data file and output directory

## Script 
- nibackgenml/preprocessing.py: copy the data 


 nibackgen3C50 rootdir='NONE' obsid='NONE'  bkgidxdir='mybgkdir' \
  bkglibdir='mybgkdir' gainepoch='2020' calevtdir='NONE' \
  ufafile='combined_ufa.evt' clfile='combined_cl.evt' \
  dtmin=10.0 dtmax=120.0
