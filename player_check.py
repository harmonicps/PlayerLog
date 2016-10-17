#!/usr/bin/env python

###########################################################
# Script: player_check.py
# Author: John Vasconcelos
# Date: 9/15/16
# Version 1.0
###########################################################

import pprint
import os
import sys, getopt
from datetime import datetime, timedelta
import time, math

secsInWeek = 604800
secsInDay = 86400
gpsEpoch = (1980, 1, 6, 0, 0, 0)  # (year, month, day, hh, mm, ss)
player_log_file = "PlayerControlAdapter.log"
dpi_pid_filter = ""

# Error List from ICD
error_list = {
    '0':'OK' , 
    '1':'Not Enough Media',
    '2':'File Not Found',
    '3':'Repeated Command',
    '4':'Play Without Prepare',
    '5':'Invalid format',
    '6':'Unsupported Format',
    '7':'Corrupt Media',
    '8':'Live Source Not Available',
    '9':'Unknown Error',
    '10':'Invalid Layer '}

# Clip Type List from ICD
clip_type_list = {
    '1':'Follow Live',
    '2':'1080p',
    '3':'1080i',
    '4':'720p',
    '5':'480i (4:3)',
    '6':'480i (16:9)'}

resp_code_list = {
    '100':'Successful',
    '101':'Not Authorized for DPI',
    '103':'DPI De-Provisioned',
    '104':'DPI not Supported',
    '105':'Duplicate Service Name',
    '110':'In Use allowready',
    '112':'Not Provisioned for DPI',
    '120':'Splice Request Failed',
    '122':'Splice Request Late',
    '124':'Unknow Error'}

def UTCFromGps(gpsWeek, SOW, leapSecs=14):
    """converts gps week and seconds to UTC

    see comments of inverse function!

    SOW = seconds of week
    gpsWeek is the full number (not modulo 1024)
    """
    secFract = SOW % 1
    epochTuple = gpsEpoch + (-1, -1, 0)
    t0 = time.mktime(epochTuple) - time.timezone  #mktime is localtime, correct for UTC
    tdiff = (gpsWeek * secsInWeek) + SOW - leapSecs
    t = t0 + tdiff
    (year, month, day, hh, mm, ss, dayOfWeek, julianDay, daylightsaving) = time.gmtime(t)
    #use gmtime since localtime does not allow to switch off daylighsavings correction!!!
    utc_time = '%s-%s-%s %s:%s:%s' %(year, month, day, hh, mm, ss + secFract)
    return utc_time


#print UTCFromGps(0,1154597417)


def get_logdata(message):
    logdata_ret = ""
    
    log_line = message[1].split(",")
    
    log_extract = log_line[0]
    
    if log_extract.strip() == '-12278':
        logdata_ret = "Prepare"
    elif log_extract.strip() == '-12287':
        logdata_ret = "Play Request"
    elif log_extract.strip() == '-12276':
        logdata_ret = "Prepare Cancel"
    elif log_extract.strip() == '-32767':
        logdata_ret = "Prepare Status"
    elif log_extract.strip() == '-32768':
        logdata_ret = "Play Status"        
    elif log_extract.strip() == '-12279':
        logdata_ret = "UMP Select" 
    elif log_extract.strip() == '257':
        logdata_ret = "Splice Request" 
    elif '}' in log_extract:
    	for char_line in log_extract:
    	    if "}" not in char_line and "]" not in char_line:
    	        logdata_ret = logdata_ret + char_line
    else:
    	logdata_ret = log_extract
    return logdata_ret

def main(argv):    
    global player_log_file
    global dpi_pid_filter
    try:
        opts, args = getopt.getopt(argv,"hi:d:",["ifile=","dpipid="])
    except getopt.GetoptError:
        print 'player_check.py -i <PlayerLog File> -d <DPI PID>'
        sys.exit(2)
    for opt, arg in opts:
        if opt == '-h':
            print 'player_check.py -i <PlayerLog File> -d <DPI PID>'
            sys.exit()
        elif opt in ("-i", "--ifile"):
            player_log_file = arg
        elif opt in ("-d", "--dpipid"):
            dpi_pid_filter = arg         

if __name__ == "__main__":
   main(sys.argv[1:])

if os.path.isfile(player_log_file): 
    f_in = open(player_log_file,"rb")
else:
    print "File %s does not Exist !" %player_log_file
    sys.exit(2)

# Print Header
print '%-12s %-15s %-15s %-8s %-6s %-7s %-8s %-12s %-14s %-14s %-12s %-17s %-20s' %("DATE" , "TIME" , "OPERATION" , "SEQ_NUM" , "EVENT" ,"DPI_PID" , "STATUS" , 'ERROR_CODE' , 'DURATION' , 'SOM' , 'CLIP_TYPE' , 'START_TIME' , 'MATERIAL ID')

for line in f_in:
    event_id = ""
    clip_type = ""
    start_time = ""
    clip_dur = ""
    clip_som = ""
    material_id = ""
    seq_num = ""

    if dpi_pid_filter and '"dpiPidIndex":' in line:
    	dpi_pid = get_logdata(line.split('"dpiPidIndex":'))

        if int(dpi_pid_filter) is not int(dpi_pid):
            continue
    
    #Use the print command below to troubleshoot any parsing issues
    #print line
    
    if 'SCTE104MultipleOperationMessage' in line:
        (log_date,log_time,junk1,junk2,junk3,junk4,junk5,junk6,log_msg) = line.split()
        op_type = get_logdata(line.split('"operations":[{"opID":'))
        dpi_pid = get_logdata(line.split('"dpiPidIndex":'))
        
        if '"seqNum":' in line:
            seq_num = get_logdata(line.split('"seqNum":'))
        if op_type == "Play Request":
            event_id = get_logdata(line.split('"eventId":'))
        if '"materialId":{"contents":' in line:
            material_id = get_logdata(line.split('"materialId":{"contents":'))
        if '"inputId":{"contents":' in line:
            material_id = get_logdata(line.split('"inputId":{"contents":'))
        if '"duration":{"contents":' in line:
            clip_dur = get_logdata(line.split('"duration":{"contents":'))
        if '"som":{"contents":' in line:
            clip_som = get_logdata(line.split('"som":{"contents":'))
        if '"clipType":' in line:
            clip_type_id = get_logdata(line.split('"clipType":'))
            clip_type = clip_type_list[clip_type_id.strip()]
        if '"utcSeconds":' in line:
            start_time_gps = get_logdata(line.split('"utcSeconds":'))
            start_time = UTCFromGps(0,int(start_time_gps))
        print '%-12s %-15s %-15s %-8s %-6s %-7s %-8s %-12s %-14s %-14s %-12s %-17s %-20s' %(log_date,log_time,op_type,seq_num,event_id,dpi_pid,'','',clip_dur,clip_som,clip_type,start_time,material_id)

    if 'UmpPrepareStatusMessage' in line or 'UmpPlayStatusMessage' in line:
        (log_date,log_time,junk1,junk2,junk3,junk4,junk5,junk6,log_msg) = line.split()
        op_type = get_logdata(line.split('{"opID":'))
        seq_num = get_logdata(line.split('"seqNum":'))
        dpi_pid = get_logdata(line.split('"dpiPidIndex":'))
        status_type = get_logdata(line.split('"statusType":'))
        error_code_id = get_logdata(line.split('"errorCode":'))
        error_code = error_list[error_code_id.strip()]
        print '%-12s %-15s %-15s %-8s %-6s %-7s %-8s %-12s' %(log_date,log_time,op_type,seq_num,'',dpi_pid,status_type,error_code)

    if 'SCTE104InitRequestMessage' in line:
        (log_date,log_time,junk1,junk2,junk3,junk4,junk5,junk6,log_msg) = line.split()
        op_type = 'INIT Request'
        dpi_pid = get_logdata(line.split('"dpiPidIndex":'))
        print '%-12s %-15s %-15s %-8s %-6s %-7s' %(log_date,log_time,op_type,'','',dpi_pid)

    if 'SCTE104InitResponseMessage' in line:
        (log_date,log_time,junk1,junk2,junk3,junk4,junk5,junk6,log_msg) = line.split()
        op_type = 'INIT Response'
        dpi_pid = get_logdata(line.split('"dpiPidIndex":'))
        result_id = get_logdata(line.split('"result":'))
        result_msg = resp_code_list[result_id]
        print '%-12s %-15s %-15s %-8s %-6s %-7s %-8s %-12s' %(log_date,log_time,op_type,'','',dpi_pid,'',result_msg)
    
    if 'SCTE104InjectResponseMessage' in line:
        (log_date,log_time,junk1,junk2,junk3,junk4,junk5,junk6,log_msg) = line.split()
        result_id = get_logdata(line.split('"result":'))
        if '100' not in result_id:
            op_type = 'INJECT Response'
            dpi_pid = get_logdata(line.split('"dpiPidIndex":'))
            result_msg = resp_code_list[result_id]
            print '%-12s %-15s %-15s %-8s %-6s %-7s %-8s %-12s' %(log_date,log_time,op_type,'','',dpi_pid,'',result_msg)

f_in.close()