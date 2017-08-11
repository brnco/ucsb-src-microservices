import urllib2
from bs4 import BeautifulSoup
from  __builtin__ import any as b_any
import re
import string
import argparse
import lxml
import pyodbc
import ast
import sys
import unittest


########################
###database functions###
########################
'''
queryCatalog takes an Alma system number and returns the MARC XML for the resource as a bs4 soup object
'''
def queryCatalog(sysNumber):
	#obsolete aleph api call
	#url = 'http://pegasus.library.ucsb.edu:5661/sba01pub?version=1.1&operation=searchRetrieve&query=rec.id=' + args.sys + '&maximumRecords=1'
	url = "https://ucsb.alma.exlibrisgroup.com/view/sru/01UCSB_INST?version=1.2&operation=searchRetrieve&schema=marcxml&query=alma.mms_tagSuppressed%3Dfalse+and+alma.mms_id%3D" + sysNumber + "%29"
	response = urllib2.urlopen(url) #do that
	xml = response.read() #gives back lovely marc xml
	soup = BeautifulSoup(xml,'lxml') #soupify it for parsing
	return soup

'''
queryFM_Single takes a sql command and returns a single row (row[0]) from FileMaker
'''	
def queryFM_Single(sqlstr,cnxn):
	cursor = cnxn.cursor()
	cursor.execute(sqlstr)
	row = cursor.fetchone()
	return row

'''
queryFM_Multi takes a sql command and returns every row from FileMaker
'''	
def queryFM_Multi(sqlstr,cnxn):
	cursor = cnxn.cursor()
	cursor.execute(sqlstr)
	rows = cursor.fetchall()
	return rows

'''
insertFM takes a sql insert command and executes it, commiting the change to the record
'''
def insertFM(sqlstr,cnxn):
	cursor = cnxn.cursor()
	cursor.execute(sqlstr)
	cnxn.commit()

	
########################
#########END############
########################


########################
#####data functions#####
########################
'''
insertHash takes a db connection and a list of id, filename, and hash and inserts thsoe values in a new row
'''
def insertHash(cnxn,**kwargs):
	sqlstr = """
		insert into File_instance(FK,filename,hash) 
		values ((select Original_Key from Audio_Originals where Original_Tape_Number like 
		'""" + kwargs['id'] + """/%'),'""" + kwargs['filename'] + """','""" + kwargs['hash'] + """')"""
	insertFM(sqlstr,cnxn)
	
'''
makeID3fromCatalogSoup takes a bs4 soup object and returns 1 or 2 lists of ID3 tags based on the MARC xml in Alma
'''	
def makeID3fromCatalogSoup(soup):
	id3list1 = []
	id3list2 =[]
	list028ind0=[]
	list028ind1=[]
	subtitle=''
	title1=''
	title2=''
	artist1=''
	artist2=''
	album=''
	date=''
	###1 SIDE OR 2###
	for sf in soup.findAll('subfield'): #find every xml tag named subfield
		if sf.parent['tag']=='740':
			title2 = sf.string.lstrip()
	###END SIDES###
	for sf in soup.findAll('subfield'):
		###TITLES###
		if sf.parent['tag']=='245': #find the subfields whose parent is the marc 245 field
			if sf['code']=='a': #marc 245 $a
				title1 = sf.string.lstrip() #assign the first title, strip non-word chars and leading spaces
			if sf['code']=='b': #marc 245 $b
				subtitle = sf.string.lstrip() #assign subtitle, strip non-word chars and leading spaces
		###PERFORMERS###
		elif sf.parent['tag']=='511':#find subfields whose parent is the marc 511 field
			match = ''
			match = re.search("by.*\(side A\)(\s|\.)",sf.string) #grip just the side A part
			if match:
				artist1 = match.group().replace("(side A)","").replace("by ","").lstrip()#lose the junk
			else:#if there is no (side A) bit
				artist1=sf.string #use the whole field value
				artist1 = re.sub(r".*by ",'',artist1)#lose everything before and including "by"
			match = ''
			match = re.search("\(side A\).*\(side B\)",sf.string) #grip if there is a side b
			if match:
				artist2 = match.group().replace("(side A) ; ","").replace("(side B)","").lstrip() #lose the junk
			elif len(title2) > 0: #if there is a title2
				artist2 = artist1 #set default artist 2 equal to artist one
				match2 = ''
				match2 = re.search(r".*;",artist2) #look if there's another artist for side 2
				if match2:
					artist2 = match2.group().replace(" ;","") #if there is, pop them in there
		###END PERFORMERS###
		###GRIP ALBUM###
		elif sf.parent['tag']==	'852': #grip the Columbia A69 part
			if sf['code']=='j':
				album = sf.string.lstrip()		
		###END ALBUM###
		###GRIP LABEL###
		elif sf.parent['tag']=='028':
			if sf.parent['ind1']=='0':
				if sf['code']=='a':
					list028ind0.append(sf.string)
			elif sf.parent['ind1']=='1':
				if sf['code']=='a':
					list028ind1.append(sf.string)
		###END LABEL###			
	###YEAR###
	for cf in soup.findAll('controlfield'):
		if cf['tag']=='008':
			date = cf.string[7:11]
	###END YEAR###
	###GET IT TOGETHER###
	if subtitle:
		title1 = title1 + subtitle
	if not title1:
		title1 = "Title Unavailable"
	id3list1.append(title1)
	if not artist1:
		artist1 = "Artist Unavailable"
	id3list1.append(artist1)
	if not date:
		date = "Date Unavailable"
	id3list1.append(date)
	if not album:
		album = "Album Unavailable"
	id3list1.append(album)
	if list028ind1:
		id3list1.append(list028ind1[0])
	else:
		id3list1.append(list028ind0[0])
	if len(title2) > 0:
		if not title2:
			title2 = "Title Unavailable"
		id3list2.append(title2)
		if not artist2:
			artist2 = "Artist Unavailable"
		id3list2.append(artist2)
		if not date:
			date = "Date Unavailable"
		id3list2.append(date)
		if not album:
			album = "Album Unavailable"
		id3list2.append(album)
		if list028ind1:
			id3list2.append(list028ind1[1])
		else:
			id3list2.append(list028ind0[0])	
	if id3list2:
		return id3list1,id3list2
	else:
		return id3list1,None
		
########################
#########END############
########################
	
if __name__ == '__main__':
    unittest.main()	