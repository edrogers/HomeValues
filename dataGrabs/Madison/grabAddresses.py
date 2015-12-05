#!/usr/bin/python

import requests
import time
#areas=[1,11,21]
areas = [area.rstrip('\n') for area in open('areaList.txt')]
for area in areas:
    userdata = {'AssessmentArea': area, 'sortBy': 'Address', 'search': 'salesByArea'}
    resp = requests.post("http://www.cityofmadison.com/assessor/property/salesbyarearesults.cfm",data=userdata)
    filename="MadisonAssessment_{}.html".format(area)
    fileout=open(filename,'wb')
    fileout.write(resp.content)
    fileout.close()
    time.sleep(10)
quit()
