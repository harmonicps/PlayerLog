#!/usr/bin/python

import os, sys
from pprint import pprint

opl_list = []
opl_temp_list = []

def opl_parse(file):
    ch_dpi =""
    if os.path.isfile(file):
        f_in = open(file,"rb")

    for line in f_in:
        
        if 'DpiPidIndexList =' in line:
            ch_dpi_line = line.split('DpiPidIndexList = ')[1]
            ch_dpi = ch_dpi_line.split(',')[0].strip('"')
        
        if '# Channel Id:' in line:
            ch_id = str(line.split('# Channel Id: Channel ')[1])
            #opl_list.append(ch_id.strip())
        
        if '# Channel Name:' in line:
            ch_name = line.split('# Channel Name: ')[1]
            #opl_list.append(ch_name.strip())

    if not ch_dpi == '':
        opl_list = [ch_dpi,'Channel ' + ch_id.strip(),ch_name.strip()]
        
    if 'opl_list' in vars() :
        return opl_list 

for opl_file in os.listdir("."):
    if opl_file.endswith(".opl"):
        opl_temp_list = opl_parse(opl_file)
        if opl_temp_list: 
           opl_list.append(opl_temp_list)

pprint(opl_list)