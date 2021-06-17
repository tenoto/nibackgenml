#!/usr/bin/env python

import os 

target_dir = "/Users/enoto/Box/Ext_101244_Extreme Natural Phenomena RIKEN Hakubi Research Team/Ext_EnotoLab/Ext_TeruakiEnoto/research/nibackgenml"

cmd = 'rsync -avz local "%s"' % target_dir
print(cmd);os.system(cmd)
