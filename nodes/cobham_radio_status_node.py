#!/usr/bin/env python

import rospy
import datetime
import urllib
import json
from std_msgs.msg import Float32

rospy.init_node('cobham_radio_status')

timestamp = datetime.datetime.utcfromtimestamp(rospy.Time.now().to_time()).isoformat()
    
while not rospy.has_param('cobham_radio_status'):
    print 'waiting for cobham parameters...'
    rospy.sleep(1)
    
cobham_params = rospy.get_param('cobham_radio_status')  

pubs = {}

lastByteCounts = {}

while not rospy.is_shutdown():
    status = urllib.urlopen(cobham_params['url'])
    data = json.loads(status.read())

    activeRadios = []

    for i in range(len(data['remoteStatus'])):
        rs = data['remoteStatus'][i]
        if rs['timeout'] > 0:
            activeRadios.append(i)
            
    for radio in activeRadios:
        rs = data['remoteStatus'][radio]
        if not radio in pubs:
            pubs[radio] = {}

        if not 'snr' in pubs[radio]:
            pubs[radio]['snr'] = {}
        for otherRadio in activeRadios:
            if otherRadio != radio:
                if not otherRadio in pubs[radio]['snr']:
                    pubs[radio]['snr'][otherRadio] = rospy.Publisher('/cobham/'+str(radio)+'/snr/'+str(otherRadio),Float32,queue_size=10)
                pubs[radio]['snr'][otherRadio].publish(rs['demodStatus']['snr'][otherRadio]/10.0)

        if not 'sigLevA' in pubs[radio]:
            pubs[radio]['sigLevA'] = {}
        for otherRadio in activeRadios:
            if otherRadio != radio:
                if not otherRadio in pubs[radio]['sigLevA']:
                    pubs[radio]['sigLevA'][otherRadio] = rospy.Publisher('/cobham/'+str(radio)+'/sigLevA/'+str(otherRadio),Float32,queue_size=10)
                pubs[radio]['sigLevA'][otherRadio].publish(rs['demodStatus']['sigLevA'][otherRadio])

        if not 'sigLevB' in pubs[radio]:
            pubs[radio]['sigLevB'] = {}
        for otherRadio in activeRadios:
            if otherRadio != radio:
                if not otherRadio in pubs[radio]['sigLevB']:
                    pubs[radio]['sigLevB'][otherRadio] = rospy.Publisher('/cobham/'+str(radio)+'/sigLevB/'+str(otherRadio),Float32,queue_size=10)
                pubs[radio]['sigLevB'][otherRadio].publish(rs['demodStatus']['sigLevB'][otherRadio])

        if not 'sigLevA0' in pubs[radio]:
            pubs[radio]['sigLevA0'] = rospy.Publisher('/cobham/'+str(radio)+'/sigLevA0',Float32,queue_size=10)
        pubs[radio]['sigLevA0'].publish(rs['demodStatus']['sigLevA0'])

        if not 'sigLevB0' in pubs[radio]:
            pubs[radio]['sigLevB0'] = rospy.Publisher('/cobham/'+str(radio)+'/sigLevB0',Float32,queue_size=10)
        pubs[radio]['sigLevB0'].publish(rs['demodStatus']['sigLevB0'])
        
        if radio in lastByteCounts:
            if not 'ipTxByteRate' in pubs[radio]:
                pubs[radio]['ipTxByteRate'] = rospy.Publisher('/cobham/'+str(radio)+'/ipTxByteRate',Float32,queue_size=10)
            pubs[radio]['ipTxByteRate'].publish((rs['ipStatus']['ipTxByteCnt']-lastByteCounts[radio])/2.0)
        lastByteCounts[radio] = rs['ipStatus']['ipTxByteCnt']
    rospy.sleep(2)
