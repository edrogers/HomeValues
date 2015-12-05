#!/usr/bin/python

import re, mmap
import sys, os

#Directory of scraped files
dirName=os.path.dirname(os.path.realpath(__file__))

#List of areas according to Madison:
areas=[1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23,24,25,26,27,28,29,30,31,32,33,34,35,36,37,38,39,40,41,42,43,44,45,46,47,48,49,50,51,52,53,54,55,56,57,58,59,60,61,62,63,64,65,67,68,69,70,71,72,73,74,75,76,77,78,79,80,81,82,83,84,85,86,87,88,89,90,91,92,93,94,95,96,97,98,99,100,101,102,103,104,105,106,107,108,109,110,111,112,113,114,1004,1011,1016,1017,1021,1022,1023,1024,1025,1026,1027,1028,1029,1030,1032,1033,1037,1038,1039,1040,1050,1051,1053,1054,1056,1062,1063,1064,1065,1068,1069,1070,1072,1073,1078,1080,1081,1083,1089,2001,2002,2003,2004,2005,2006,2008,2009,2010,2011,2012,2013,2014,2015,2016,2017,2018,2020,2021,2022,2023,2024,2025,2026,2027,2028,2029,2030,2031,2032,2033,2034,2036,2037,2038,2039,2040,2041,2042,2043,2044,2045,2046,2047,2048,2050,2051,2053,2054,2055,2056,2060,2061,2062,2063,2064,2065,2067,2068,2069,2070,2071,2073,2076,2078,2080,2081,2083,2085,2087,2088,2089,2090,2091,2092,2093,2094,2095,2096,2097,2098,2099,2101,2102,2103,2107,3101,3102,3103,3104,3105,3106,3107,3108,3109,3110,3111,3112,3113,3115,3117,4001,4002,4011,4012,4013,4014,5002,5003,5008,5009,5012,5013,5015,5016,5017,5018,5020,5021,5023,5024,5025,5026,5027,5028,5032,5037,5038,5043,5045,5046,5050,5051,5053,5054,5055,5060,5061,5062,5063,5064,5065,5067,5069,5073,5076,5077,5080,5082,5083,5084,5085,5086,5087,5088,5089,5092,5093,5094,5095,5096,5097,5098,5099,5100,5101,5102,5103,5105,5106,5107,5108,5109,5110,5111,5113,5204,5205,5208,5209,5211,5212,5213,5214,5226,5227,5229,5231,5232,5237,5238,5242,5243,5244,5246,5250,5251,5254,5262,5267,5273,5276,5282,5288,5294,5296,5297,5299,5421,5426,5512,5513,5526,5530,5540,5560,5561,5563,5565,5576,5577,5596,5599,5609,5612,5694,5704,5709,5711,5712,5723,5725,5730,5771,5785,5794,5796,5804,5809,5811,5812,5830,5842,5867,5885,5894,5896,5904,5908,5909,5911,5912,5913,5923,5924,5925,5930,5931,5942,5943,5952,5967,5985,5986,5994,5996]

csvFileName="assessments.csv"
csvFile=open(csvFileName,'w')
csvHeader = "address,style,stories,yearbuilt,livingarea1,bedrooms,basement,garage1,saledate,salesprice,parcelnumber,units,livingarea2,fullbaths,garage2,livingarea3,halfbaths,attic"
print >> csvFile, csvHeader

# Each record in each file begins with this specific HTML tag:
p1=re.compile(r'<tr valign="top">')
# Records themselves can be broken into lists, split at HTML tags.
#    This splits
#        </td><td width=10%>Cape Cod</td>
#    into:
#        /td
#        td width=10%
#        Cape Cod
#        /td
p2=re.compile("[<>]")

# Keep track of which indices are actually used for data at least once
#   over the entire dataset
nontrivialIndexTest=[False]*138

indicesOfInterest=[2, 6, 10, 14, 18, 22, 26, 30, 34, 38, 46, 54, 62, 66, 74, 106, 110, 114]

#computedIndicesOfInterest will merely use nonTrivialIndexTest to identify which parts
# of the HTML file should be included in homeData
computedIndicesOfInterest=[]

for area in areas:
# numbers=[0]
# for number in numbers:
#     area=102
    htmlFilename="MadisonAssessment_{}.html".format(area)
    filePath="{}/{}".format(dirName,htmlFilename)
    print filePath

    #  Open each file and break the text up into records
    with open(filePath,'r+') as f:
        #mmap prevents the fulltext from being pulled to memory all at once
        fulltext=mmap.mmap(f.fileno(),0)

        if fulltext.find("No Sales information is available for this Area") != -1:
            print "No Sales Here"
            continue
        
        records=p1.split(fulltext)

        # preamble and postamble should be cropped
        #  preamble
        records.pop(0) 
        #  postamble
        #    Need to split at "InstanceEndEditable" tag and pop off one instance of </div>
        #    to make last record have the same number of <> chars as the rest
        lastRecordWithPostamble=records[-1].split(r'<!-- InstanceEndEditable -->',1)
        lastRecordWithOneExtraTag=lastRecordWithPostamble[0]
        lastRecord=lastRecordWithOneExtraTag.rsplit(r'</div>',1)[0]
        records[-1]=lastRecord
    
        for record in records:
            #some records have extra <br> tags which need to be removed
            nbrecord1 = record.replace(r'<br>','')
            #also removing unnecessary blankspace chars
            nbrecord2 = nbrecord1.replace(r'&nbsp;',' ')

            items=p2.split(record)
            nbitems=p2.split(nbrecord2)

            #homeData will be a list containing only relevant fields for passing to the database
            homeData=[]

            regularExpressionList=[]
            regularExpressionList.append('^[-)(\'a-zA-Z0-9\s\\\\]+$')    #NON-EMPTY Address (alphanumerics [minus underscore] and whitespace)
            regularExpressionList.append('^[-a-zA-Z0-9\s]*$')        #          Style (alphanumerics [minus underscore] and whitespace)
            regularExpressionList.append('^[\d]+$')                  #NON-EMPTY Stories (digit[s])
            regularExpressionList.append('^\d\d\d\d$')               #NON-EMPTY Year Built (4 digit number)
            regularExpressionList.append('^[\d]+$')                  #NON-EMPTY Living Area 1st (digit[s])
            regularExpressionList.append('^[\d]+$')                  #NON-EMPTY Bedrooms (digits)
            regularExpressionList.append('^[\d]*$')                  #          Finished Basement (digits)
            regularExpressionList.append('^[\d]*$')                  #          Garage 1 sq ft (digits)
            regularExpressionList.append('^[\d]{4,4}-[\d]{2,2}-01$') #NON-EMPTY Sale Date (YYYY-MM-DD)
            regularExpressionList.append('^[\d]+$')                  #NON-EMPTY Sales Price (digits)
            regularExpressionList.append('^[\d]+$')                  #NON-EMPTY Parcel Number (digits)
            regularExpressionList.append('^[\d]+$')                  #NON-EMPTY Units (digits)                
            regularExpressionList.append('^[\d]*$')                  #          Living Area 2nd floor (digits)
            regularExpressionList.append('^[\d]+$')                  #NON-EMPTY Full Baths (digits)
            regularExpressionList.append('^[\d]*$')                  #          Garage 2 sq ft (digits)
            regularExpressionList.append('^[\d]*$')                  #          Living Area 3rd floor (digits)
            regularExpressionList.append('^[\d]*$')                  #          Half Baths (digits)
            regularExpressionList.append('^[\d]*$')                  #          Finished Attic (digits)

            #Rewrite each item to prepare for database entry
            for ni, i in enumerate(indicesOfInterest):
                if   ni==6:
                    nbitems[i]=nbitems[i].strip().rstrip(' bas')
                elif ni==7 or ni==14:
                    nbitems[i]=nbitems[i].strip().lstrip('DAtachedBsmn ')
                elif ni==8:
                    dateRE=re.compile('^\d{1,2}/\d{4,4}$')
                    normalDate=dateRE.match(nbitems[i].strip())
                    if normalDate:
                        monthRE=re.compile('^\d{1,2}')
                        yearRE =re.compile('\d{4,4}$')
                        month=monthRE.match(nbitems[i].strip()).group().zfill(2)
                        year =yearRE.search(nbitems[i].strip()).group()
                        nbitems[i]='{}-{}-01'.format(year,month)
                elif ni==9:
                    nbitems[i]=nbitems[i].strip().replace('$','').replace(',','')

                if nbitems[i].strip()!='':
                    if nbitems[i].strip().find("'"):
                        nbitems[i] = nbitems[i].strip().replace("'","\\'")
                    homeData.append("{}".format(nbitems[i].strip()))
                else :
                    homeData.append("N/A")

                #Check if data is ready for entry:
                wellFormedDataEntry=re.match(regularExpressionList[ni],nbitems[i].strip())
                # if ni==17:
                if not wellFormedDataEntry:
                    print ""
                    print "Address                 == {}".format(homeData[0])
                    print "Style                   == {}".format(homeData[1])
                    print "Stories                 == {}".format(homeData[2])
                    print "Year Built              == {}".format(homeData[3])
                    print "Living Area 1st floor   == {}".format(homeData[4])
                    print "Bedrooms                == {}".format(homeData[5])
                    print "Finished Basement       == {}".format(homeData[6])
                    print "Garage 1 sq ft          == {}".format(homeData[7])
                    print "Sale Date               == {}".format(homeData[8])
                    print "Sales Price             == {}".format(homeData[9])
                    print "Parcel Number           == {}".format(homeData[10])
                    print "Units                   == {}".format(homeData[11])
                    print "Living Area 2nd floor   == {}".format(homeData[12])
                    print "Full Baths              == {}".format(homeData[13])
                    print "Garage 2 sq ft          == {}".format(homeData[14])
                    print "Living Area 3rd floor   == {}".format(homeData[15])
                    print "Half Baths              == {}".format(homeData[16])
                    print "Finished Attic          == {}".format(homeData[17])
            
            if homeData[0]=="'4751 Bellingrath St'":
                homeData[4]=984
                homeData[12]=1246
#                print "Error Corrected"
                                
            print >> csvFile, "{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{}".format(
                      homeData[0],
                      homeData[1],
                      homeData[2],
                      homeData[3],
                      homeData[4],
                      homeData[5],
                      homeData[6],
                      homeData[7],
                      homeData[8],
                      homeData[9],
                      homeData[10],
                      homeData[11],
                      homeData[12],
                      homeData[13],
                      homeData[14],
                      homeData[15],
                      homeData[16],
                      homeData[17]);
                    
            boringItems=(r'table',
                         r'tbody',
                         r'tr',
                         r'td',
                         r'/td',
                         r'/tr',
                         r'/tbody',
                         r'/table',
                         r'/div')
            for i, item in enumerate(nbitems):
                item=item.strip()
                if item and not (item.startswith(boringItems)):
                    #            print i, item
                    nontrivialIndexTest[i]=True


            for i, item in enumerate(nbitems):
                item=item.strip()
                #        print i, item

csvFile.close()
        
#print indicesOfInterest

for i, j in enumerate(nontrivialIndexTest):
    if j:
        computedIndicesOfInterest.append(i)

#print computedIndicesOfInterest
#print len(computedIndicesOfInterest)
quit()
