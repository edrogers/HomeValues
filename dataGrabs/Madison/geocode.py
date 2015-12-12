#!/usr/bin/python
#
#########################################################################################
# geocode.py - Ed Rogers - 18 Mar 2015
#
#   After scraping data that includes an address from a municipal website and storing
# it in a MySQL DB table named "assessments", geocode each address, 2500 addresses per
# day, using Google's Geocoding API. The first Lat & Lng results reported are stored
# in a separate table, "geocodes".
#   This code is intended to be run daily from a cron job, which will remove itself
# from the crontab after it has geocoded each address
#
#########################################################################################

import MySQLdb as mdb
import sys
import simplejson, urllib
import time
import subprocess
import re
import config

maxToProcessInADay=2500
removeJobFromCrontab=False

try:
        con = mdb.connect('localhost', config.mySQLUser,config.mySQLPass,'madvalues')
        cur = con.cursor()

        execStatement="SELECT COUNT(*) FROM assessments;"
        cur.execute(execStatement)
        nTotalRowsToProcessRow = cur.fetchall()
        nTotalRowsToProcess=nTotalRowsToProcessRow[0][0]
        execStatement="SELECT COUNT(*) FROM geocodes;"
        cur.execute(execStatement)
        nAlreadyProcessedRow = cur.fetchall()
        nAlreadyProcessed=nAlreadyProcessedRow[0][0]

        nRemainingToProcess=nTotalRowsToProcess-nAlreadyProcessed
        rowToStart=nAlreadyProcessed+1

        if nRemainingToProcess > maxToProcessInADay:
                nRowsToProcessToday=maxToProcessInADay
        else:
                nRowsToProcessToday=nRemainingToProcess
                removeJobFromCrontab=True
                
        execStatement="SELECT id,address FROM assessments WHERE id>={} AND id<{};".format(rowToStart,rowToStart+nRowsToProcessToday)
        cur.execute(execStatement)
        assessmentRows = cur.fetchall()

        lastAddressChecked=""
        delimitedAddress=""
        lat=0
        lng=0
        locationType=""
        for assessmentRow in assessmentRows:
            rawAddress=assessmentRow[1].strip()
            if lastAddressChecked != rawAddress:
                lastAddressChecked=rawAddress
                delimitedAddress=rawAddress.replace("'","\\'")
                addressString="{}, Madison, WI".format(rawAddress).replace(" ","+")
                urlBase="https://maps.googleapis.com/maps/api/geocode/json"
                parameters="address={}&key={}".format(addressString,config.googleAPIKey)
                url="{}?{}".format(urlBase,parameters)
                print "DEBUG: URL request pending: simplejson.load(urllib.urlopen({}))".format(url)
                time.sleep(1)
                result=simplejson.load(urllib.urlopen(url))
                        
                status=result['status']
                if status=="OK":
                    lat=result['results'][0]['geometry']['location']['lat']
                    lng=result['results'][0]['geometry']['location']['lng']
                    locationType=result['results'][0]['geometry']['location_type']
        #            print "status: {}, assessment_id: {}, address: {}, lat: {}, lng: {}, locationType: {}".format(status,assessmentRow[0],assessmentRow[1],lat,lng,locationType)
                    execStatement="INSERT INTO geocodes " + \
                    "(assessment_id,address,lat,lng,location_type)" + \
                    " VALUES ({},'{}',{},{},'{}')".format(
                        assessmentRow[0],
                        delimitedAddress,
                        lat,lng,locationType)
                    print "DEBUG: SQL statement pending: cur.execute({})".format(execStatement)
                    cur.execute(execStatement)
                    con.commit()
            else:
                execStatement="INSERT INTO geocodes " + \
                "(assessment_id,address,lat,lng,location_type)" + \
                " VALUES ({},'{}',{},{},'{}')".format(
                    assessmentRow[0],
                    delimitedAddress,
                    lat,lng,locationType)
                print "DEBUG: SQL statement pending: cur.execute({})".format(execStatement)
                cur.execute(execStatement)
                con.commit()

except mdb.Error, e:
        print "Error %d: %s" % (e.args[0],e.args[1])
        sys.exit(1)
finally:
        if con:
            con.close()

if removeJobFromCrontab:
    lineBreaks=re.compile("\n")
    thisJob=re.compile(r'geocode.py')
    currentCrontab=subprocess.check_output(["crontab", "-l"])
    newCrontab=open("newCrontab.txt",'wb')
    cronJobs=lineBreaks.split(currentCrontab)
    for cronJob in cronJobs:
        if thisJob.search(cronJob) == None:
            newCrontab.write(cronJob+"\n")
    newCrontab.close()
    subprocess.call(["crontab","-r"])
    subprocess.call(["crontab","-i","newCrontab.txt"])
    subprocess.call(["rm","newCrontab.txt"])
            
quit
