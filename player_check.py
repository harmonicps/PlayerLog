#!/usr/bin/python

###########################################################
# Script: player_check.py
# Author: John Vasconcelos
# Date: 10/17/16
# Version 2.0
###########################################################

from pprint import pprint
import os
import sys, getopt
from datetime import datetime, timedelta
import time, math
import socket
import json

secsInWeek = 604800
secsInDay = 86400
gpsEpoch = (1980, 1, 6, 0, 0, 0)  # (year, month, day, hh, mm, ss)
player_log_file = "PlayerControlAdapter.log"
dpi_pid_filter = ""
host_name = socket.gethostname()
is_error_only = False
opl_list = []

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

optype_list = {
    '-12278':'Prepare',
    '-12287':'Play Request',
    '-12276':'Prepare Cancel',
    '-32767':'Prepare Status',
    '-32768':'Play Status',
    '-12279':'UMP Select',
    '-12280':'UMP Stop',
    '-12281':'Insert Template',
    '-12283':'Insert Graphic',
    '257':'Splice Request',
    '1':'INIT Request',
    '2':'INIT Response'}

# Clip Type List from ICD
play_status_list = {
    1:'Start',
    2:'End',
    3:'ERROR'}

# Clip Type List from ICD
prep_status_list = {
    1:'Prepared',
    2:'Cancel',
    3:'ERROR'}

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
    '''
    Extracts the needed output to be loaded into the print variables
    '''
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

def get_multipleop(dict_log,op_id,dict_key):

    '''
    Extracts the log from the dictionary
    '''
    ret_value = ''

    # Get log info for a Play Request
    if op_id == '-12287':
        if dict_key == 'seqNum':
            ret_value = dict_log['operations'][0]['data']['clips'][0]['seqNum']
        elif dict_key == 'eventId':
            ret_value = dict_log['operations'][0]['data']['clips'][0]['eventId']
        elif dict_key == 'duration':
            ret_value = dict_log['operations'][0]['data']['clips'][0]['duration']['contents']
        elif dict_key == 'som':
            ret_value = dict_log['operations'][0]['data']['clips'][0]['som']['contents']
        elif dict_key == 'clipType':
            ret_value = dict_log['operations'][0]['data']['clips'][0]['clipType']
        elif dict_key == 'materialId':
            ret_value = dict_log['operations'][0]['data']['clips'][0]['materialId']['contents']

    # Get log info for a Prepare Command
    elif op_id == '-12278':
        if dict_key == 'seqNum':
            ret_value = dict_log['operations'][0]['data']['clipInfo'][0]['seqNum']
        elif dict_key == 'eventId':
            ret_value = dict_log['operations'][0]['data']['clipInfo'][0]['eventId']
        elif dict_key == 'duration':
            ret_value = dict_log['operations'][0]['data']['clipInfo'][0]['duration']['contents']
        elif dict_key == 'som':
            ret_value = dict_log['operations'][0]['data']['clipInfo'][0]['som']['contents']
        elif dict_key == 'materialId':
            ret_value = dict_log['operations'][0]['data']['clipInfo'][0]['materialId']['contents']

    # Get log info for a UMP Select Command
    elif op_id == '-12279':
        if dict_key == 'seqNum':
            ret_value = dict_log['operations'][0]['data']['seqNum']
        elif dict_key == 'inputId':
            ret_value = dict_log['operations'][0]['data']['inputId']['contents']
        elif dict_key == 'eventId':
            ret_value = dict_log['operations'][0]['data']['eventId']        
    
    # Get log info for a UMP Insert Template or Insert Graphic or UMP Stop
    elif (op_id) == '-12281' or '-12283' or '-12280':
        if dict_key == 'seqNum':
            ret_value = dict_log['operations'][0]['data']['seqNum']
        elif dict_key == 'duration':
            ret_value = dict_log['operations'][0]['data']['duration']['contents']
        elif dict_key == 'eventId':
            ret_value = dict_log['operations'][0]['data']['eventId']
        elif dict_key == 'materialId':
            ret_value = dict_log['operations'][0]['data']['materialId']['contents']
        elif dict_key == 'layer':
            ret_value = dict_log['operations'][0]['data']['layer']

    # Get log info for a Prepare Cancel Command
    elif op_id == '-12276':
        if dict_key == 'seqNum':
            ret_value = dict_log['operations'][0]['data']['seqNum']

    else:
        ret_value = 'N/A'

    return ret_value

def opl_parse(file):
    if os.path.isfile(file):
        f_in = open(file,"rb")

    for line in f_in:
        if '# Channel Id:' in line:
            ch_id = str(line.split('# Channel Id: Channel ')[1])

 
def main(argv):    
    global player_log_file
    global dpi_pid_filter
    global is_error_only
    try:
        opts, args = getopt.getopt(argv,"hef:d:",["ifile=","dpipid="])
    except getopt.GetoptError:
        print 'player_check.py -f <PlayerLog File> -d <DPI PID> -e [show errors only]'
        sys.exit(2)
    for opt, arg in opts:
        if opt == '-h':
            print 'player_check.py -f <PlayerLog File> -d <DPI PID> -e [show errors only]'
            sys.exit()
        elif opt in ("-f", "--ifile"):
            player_log_file = arg
        elif opt in ("-d", "--dpipid"):
            dpi_pid_filter = arg        
        if opt == '-e':
            is_error_only = True

if __name__ == "__main__":
   main(sys.argv[1:])

# Get list of Channel ID DPI PID and Channel Name
for opl_file in os.listdir("."):
    if file.endswith(".opl"):
        opl_list.append(opl_parse(file))


if os.path.isfile(player_log_file): 
    f_in = open(player_log_file,"rb")
else:
    print "File %s does not Exist !" %player_log_file
    sys.exit(2)

# Print Header
print '\n\n'
print '*' * 40
print 'Processing {} for Encoder:'.format(player_log_file)
print '{:>20}'.format(host_name)
print '*' * 40
print '\n'

print '%-12s %-15s %-15s %-8s %-6s %-7s %-8s %-12s %-14s %-14s %-12s %-17s %-20s' %("DATE" , "TIME" , "OPERATION" , "SEQ_NUM" , "EVENT" ,"DPI_PID" , "STATUS" , 'ERROR' , 'DURATION' , 'SOM' , 'CLIP_TYPE' , 'START_TIME' , 'MATERIAL ID')


# Check Logfile Line by Line
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
        
        log_date = line.split()[0]

        log_time = line.split()[1]

        str_msg = line.split('SCTE104MultipleOperationMessage ')

        str_dict = json.loads(str_msg[1])

        dpi_pid = str_dict['dpiPidIndex']

        #Loads the Op Type into the variable.
        if '"opID":' in line:
            op_id = str(str_dict['operations'][0]['opID'])
            if op_id in optype_list:
                op_type = optype_list[op_id]
            else:
                op_type = op_id
        
        if '"seqNum":' in line:
            seq_num = get_multipleop(str_dict,op_id,'seqNum')
        if '"eventId":' in line:
            event_id = get_multipleop(str_dict,op_id,'eventId')    
        if '"materialId":{"contents":' in line:
            material_id = get_multipleop(str_dict,op_id,'materialId')
        if '"inputId":{"contents":' in line:
            material_id = get_multipleop(str_dict,op_id,'inputId')
        if '"duration":{"contents":' in line:
            clip_dur = get_multipleop(str_dict,op_id,'duration')
        if '"som":{"contents":' in line:
            clip_som = get_multipleop(str_dict,op_id,'som')
        if '"layer":' in line:
            clip_type = 'Layer %s' %get_multipleop(str_dict,op_id,'layer')
        if '"clipType":' in line:
            clip_type_id = str(get_multipleop(str_dict,op_id,'clipType'))
            clip_type = clip_type_list[clip_type_id]
        if '"utcSeconds":' in line:
            start_time_gps = str_dict['timestamp']['utcSeconds']
            start_time = UTCFromGps(0,int(start_time_gps))
        
        if not is_error_only:
            print '%-12s %-15s %-15s %-8s %-6s %-7s %-8s %-12s %-14s %-14s %-12s %-17s %-20s' %(log_date,log_time,op_type,seq_num,event_id,dpi_pid,'','',clip_dur,clip_som,clip_type,start_time,material_id)


    if 'UmpPrepareStatusMessage' in line or 'UmpPlayStatusMessage' in line:

        log_date = line.split()[0]

        log_time = line.split()[1]

        if 'UmpPrepareStatusMessage' in line:
            str_msg = line.split('UmpPrepareStatusMessage ')
        else:
            str_msg = line.split('UmpPlayStatusMessage ')
        

        str_dict = json.loads(str_msg[1])

        #Loads the Op Type into the variable.
        op_id = str(str_dict['opID'])
        if op_id in optype_list:
            op_type = optype_list[op_id]
        else:
            op_type = op_id

        dpi_pid = str_dict['data']['dpiPidIndex']
        seq_num = str_dict['data']['seqNum']
        status_id = str_dict['data']['statusType']
        
        if op_id == '-32768':
            status_type = play_status_list[status_id]
        elif op_id == '-32767':
            status_type = prep_status_list[status_id]
        else:
            status_type = status_id

        error_code_id = str(str_dict['data']['errorCode'])
        error_code = error_list[error_code_id.strip()]

        if '"eventId":' in line:
            event_id = str_dict['data']['eventId']

        if is_error_only:
            if status_type == 'ERROR':
               print '%-12s %-15s %-15s %-8s %-6s %-7s %-8s %-12s' %(log_date,log_time,op_type,seq_num,event_id,dpi_pid,status_type,error_code)
        else:
            print '%-12s %-15s %-15s %-8s %-6s %-7s %-8s %-12s' %(log_date,log_time,op_type,seq_num,event_id,dpi_pid,status_type,error_code)

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
            status_type = "ERROR"
            dpi_pid = get_logdata(line.split('"dpiPidIndex":'))
            result_msg = resp_code_list[result_id]
            print '%-12s %-15s %-15s %-8s %-6s %-7s %-8s %-12s' %(log_date,log_time,op_type,'','',dpi_pid,status_type,result_msg)

    if 'not equal hostname' in line:
        
        log_date = line.split()[0]

        log_time = line.split()[1]

        result_msg = line.split('  - ')[1]

        status_type = "ERROR"

        print '%-12s %-15s %-15s %-8s %-6s %-7s %-8s %-12s' %(log_date,log_time, "Prepare" ,"", "","",status_type,result_msg)



f_in.close()