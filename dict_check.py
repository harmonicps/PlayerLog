#!/usr/bin/env python

import json
from pprint import pprint
import os, sys

f = []

for file in os.listdir("."):
    if file.endswith(".opl"):
        f.append(file)

print f

s = '{"time":{"seconds":1466585227,"microseconds":41000},"spliceInfoSection":{"tableId":252,"sectionSyntaxIndicator":false,"privateIndicator":false,"reserved":3,"protocolVersion":0,"encryptedPacket":false,"encryptionAlgorithm":0,"ptsAdjustment":0,"cwIndex":-1,"tier":4095,"spliceCommand":{"spliceEventId":1,"spliceEventCancelIndicator":false,"outOfNetworkIndicator":true,"programSpliceFlag":true,"durationFlag":false,"spliceImmediateFlag":false,"spliceTime1":{"timeSpecifiedFlag":true,"ptsTime":163883392},"uniqueProgramId":8,"availNum":0,"availsExpected":0},"descriptors":{"descriptorList":[]},"alignmentStuffing":[],"eCrc32":0,"crc32":2629977560,"sectionData":[0,0,0,0,0,0,-1,-1,-16,15,5,0,0,0,1,127,-49,-2,9,-60,-87,-128,0,8,0,0,0,0,-100,-62,69,-40],"checkCRC":false,"checkSectionLength":false},"msgID":{"messageID":12},"result":{"value":65535},"resultExtension":65535}'

#l = '2016-06-22 08:28:30,117 [Thread-1130743] INFO  com.harmonicinc.ump.server.AS104ConnectionLogger  - Received SCTE104MultipleOperationMessage {"reserved":-1,"protocolVersion":0,"asIndex":0,"messageNumber":0,"dpiPidIndex":103,"SCTE35ProtocolVersion":0,"timestamp":{"utcSeconds":1150622806,"utcMicroseconds":2824,"timeType":1},"operations":[{"opID":-12278,"data":{"dpiPidIndex":103,"umpId":{"contents":"ENG-ENC-02-P","byteContent":[69,78,71,45,69,78,67,45,48,50,45,80,0,0],"size":14},"clipInfo":[{"seqNum":6368,"materialId":{"contents":"/2109f8ab-fbeb-4dc7-8746-2b7c896e5fc5/1/SKSP-005590750_OMN0607195109.mpg","byteContent":[47,50,49,48,57,102,56,97,98,45,102,98,101,98,45,52,100,99,55,45,56,55,52,54,45,50,98,55,99,56,57,54,101,53,102,99,53,47,49,47,83,75,83,80,45,48,48,53,53,57,48,55,53,48,95,79,77,78,48,54,48,55,49,57,53,49,48,57,46,109,112,103,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],"size":255},"duration":{"contents":"00:00:30.00","byteContent":[48,48,58,48,48,58,51,48,46,48,48],"size":11},"som":{"contents":"00:00:00.00","byteContent":[48,48,58,48,48,58,48,48,46,48,48],"size":11}}]}}]}'

#li = l.split()

d = json.loads(s)

#pprint(d)

'''
op = d['operations'][0]['opID']
dpi_pid = d['dpiPidIndex']

cliptype = d['operations'][0]['data']['clips'][0]['clipType']
material = d['operations'][0]['data']['clips'][0]['materialId']['contents']

#Play Request
seq = d['operations'][0]['data']['clips'][0]['seqNum']
event = d['operations'][0]['data']['clips'][0]['eventId']
dur = d['operations'][0]['data']['clips'][0]['duration']['contents']
som = d['operations'][0]['data']['clips'][0]['som']['contents']


#Prepare, Play Request
time_stamp = d['timestamp']['utcSeconds']


#Prepare
material = d['operations'][0]['data']['clipInfo'][0]['materialId']['contents']
dur = d['operations'][0]['data']['clipInfo'][0]['duration']['contents']
seq = d['operations'][0]['data']['clipInfo'][0]['seqNum']
event = d['operations'][0]['data']['clipInfo'][0]['eventId']
dur = d['operations'][0]['data']['clipInfo'][0]['duration']['contents']
som = d['operations'][0]['data']['clipInfo'][0]['som']['contents']

#UMPInput Select
inputid = d['operations'][0]['data']['inputId']['contents']

#UMPInput Select, Prepare Cancel
seq = d['operations'][0]['data']['seqNum']

optype_list = {
    '-12278':'Prepare',
    '-12287':'Play Request',
    '-12276':'Prepare Cancel',
    '-32767':'Prepare Status',
    '-32768':'Play Status',
    '-12279':'UMP Select',
    '257':'Splice Request'}



print cliptype
print op
print material
print seq
print event
print dur
print som
print time_stamp
'''