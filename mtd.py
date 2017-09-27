import urllib2
from bs4 import BeautifulSoup
from  __builtin__ import any as b_any
import re
import os
import string
import argparse
import lxml
import pyodbc
import sys
import time
import struct
import binascii
import random
import unittest
###UCSB modules###
import util as ut
import logger as log
import makestartobject as makeso

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
def queryFM_single(sqlstr,cnxn):
	cursor = cnxn.cursor()
	cursor.execute(sqlstr)
	row = cursor.fetchone()
	return row

'''
queryFM_Multi takes a sql command and returns every row from FileMaker
'''	
def queryFM_multi(sqlstr,cnxn):
	cursor = cnxn.cursor()
	cursor.execute(sqlstr)
	rows = cursor.fetchall()
	return rows

'''
insertFM takes a sql insert command and executes it, committing the change to the record
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
	if kwargs['materialType'] is 'tape':
		sqlstr = """insert into
			File_instance(FK,filename,hash) 
			values ((select Original_Key from Audio_Originals where Original_Tape_Number like 
			'""" + kwargs['id'] + """/%'),'""" + kwargs['filename'] + """','""" + kwargs['hash'] + """')"""
	elif kwargs['materialType'] is 'video':
		sqlstr = """insert into
				file_instance(PK,filename,hash)
				values ((select Original_Key from Visual_Originals where Original_Tape_Number like
				'""" + kwargs['id'].capitalize() + """/%'),'""" + kwargs['filename'] + """','""" + kwargs['hash'] + """')"""
	insertFM(sqlstr,cnxn)

'''
get_hash_fromFM returns the stored hash for the supplied filename
'''
def get_hash_fromFM(cnxn,**kwargs):
	if kwargs['materialType'] is 'tape':
		sqlstr = """select
					hash from File_instance
					where filename = '""" + kwargs['filename'] + "'"
	elif kwargs['materialType'] is 'video':
		sqlstr = """select
					hash from file_instance
					where filename = '""" + kwargs['filename'] + "'"
	hash = queryFM_single(sqlstr,cnxn)
	if hash:
		hash = hash[0]
	else:
		hash = None
	return hash
	
'''
makebext_umid generates a 64byte string of numbers base on SMPTE 330M to use as a UMID. Second-half is zeroed out, we use this to validate every wave as bext v1
'''
def makebext_umid():
	universal_label = '060A2B340101010101010211'
	length = '13'
	instance = '000000'
	material_number = '00000000000000000000000000000000'
	umid = '--UMID=' + universal_label + length + instance + material_number
	bext_umid = "--UMID=" + umid
	return umid

'''
makebext_description_parse_result takes the result of the FM query and transforms it into a string that can be read by BWFMetaEdit
'''
def makebext_description_parse_result(result,fieldlist):
	x = {}
	if result is not None:
		bext_description = "--Description="
		if isinstance(result, ut.dotdict):
			for key in result:
				bext_description = bext_description + key + ":" + str(result[key]) + ";"
		else:
			count = 0 #init a counter
			while count < len(fieldlist): #loop the same # of times as the field list is long
				if result[count]: #if there's a value in the field
					if count == 0:
						x[fieldlist[count]]=str(int(result[count]))
					else:	
						x[fieldlist[count]]=result[count] #set the FileMakerField:FileMakerValue pair according to the index
				else: #Nonetypes can't be assigned directly
					x[fieldlist[count]]="None"
				bext_description = bext_description + fieldlist[count] + ":" + str(x[fieldlist[count]]) + ";"
				count=count+1
		return bext_description
	elif result is None:
		return None

'''
makebext_description is a handler for generating a bext description string that can be read by BWFMetaEdit
'''
def makebext_description(cnxn,args):
	x = {} #dictionary for the resulting FileMakerField:FileMakerValue pairs
	if args.aNumber:
		fieldlist = ["Master_Key","Tape_Title","Mss_Number","Collection_Name","Master_Key"] #fields to select in FileMaker
		sqlstr = """select 
			ao.Master_Key, ao.Tape_Title, ao.Mss_Number, ao.Collection_Name, ao.Mastered
			from Audio_Originals ao
			join Audio_Masters am
			on ao.Original_Key=am.Original_Key
			where ao.Original_Tape_Number like '""" + args.aNumber.upper() + "/%'"
		result = queryFM_single(sqlstr,cnxn)
		bext_description = makebext_description_parse_result(result,fieldlist)
	elif args.cylNumber:
		fieldlist = ["PK","Label_Cat","Title","Performer","yr"]
		sqlstr = """select
			PK, Label_Cat, Title, Performer, yr
			from Cylinders
			where Call_Number_asText = '""" + args.cylNumber + "'"
		result = queryFM_single(sqlstr,cnxn)
		bext_description = makebext_description_parse_result(result,fieldlist)		
	elif args.discID: 
		soup = queryCatalog(args.discID)
		l1, l2 = makeID3fromCatalogSoup(soup)
		if args.side.lower() == "a":
			result = l1
		elif args.side.lower() == "b":
			result = l2
		bext_description = makebext_description_parse_result(result,None)
	return bext_description.replace(" ","")

'''
makebext_complete is a handler to generate a bext string that can be read by BWFMetaEdit
'''	
def makebext_complete(cnxn,**kwargs):
	args = ut.dotdict(kwargs)
	bext_description = makebext_description(cnxn,args)
	if args.aNumber:
		bext_originatorReference = "cusb-" + args.aNumber
	elif args.cylNumber:
		bext_originatorReference = "cusb-cyl" + args.cylNumber
	elif args.discID:
		bext_originatorReference = args.discBarcode.replace("ucsb","cusb")
	if args.bextVersion == '1':
		umid = makebext_umid()
	else:
		umid = ''
	bextstr = "--Originator=US,CUSB,SRC --originatorReference="+ bext_originatorReference + " " + bext_description + " " + umid
	try:
		bext = bextstr.encode('utf-8')
	except:
		bext = bextstr
	return bext

'''
get_aNumber_channelConfig_face formats a query for FM to grip a tape's aNumber, channel configuration, and face, from that's tape's rawCaptureName in new_ingest
returns list of [aNumber,channelConfig,face] e.g., ["a1234","1/4-inch Half Track Mono","fAB"]
'''
def get_aNumber_channelConfig_face(cnxn,**kwargs):
	args = ut.dotdict(kwargs)
	facelist = ["fAB","fCD"]
	nameFormat = {}
	row = ''
	count = 0
	cnxn = pyodbc.connect(cnxn)
	while not row: #try to find the Tape Number and Format based on the rawCaptureName
		if count > 1: 
			return None
		else:
			sqlstr="""select Audio_Originals.Tape_Number, Audio_Originals.Original_Recording_Format 
					from Audio_Originals join Audio_Masters on Audio_Originals.Original_Key=Audio_Masters.Original_Key 
					where Audio_Masters.rawCaptureName_""" + facelist[count] + "='" + args.rawcapNumber + "' or Audio_Masters.rawCaptureName_" + facelist[count] + "='" + args.rawcapNumber + ".wav'"
			#OR above necessary because sometimes the rawCaptureName has a ".wav" at the end :(
			row = queryFM_single(sqlstr,cnxn)
			face = facelist[count] #assign this now, if we assign at bottom of loop, count = count + 1 and it'll be the wrong index
			count = count+1
	if row:
		#print row
		nameFormat["aNumber"] = row[0]
		nameFormat["face"] = face
		#rowstr = str(row) #convert to string
		if any("Cassette" in s for s in row): #if the rawCaptureName is of a cassette tape
			nameFormat["channelConfig"] = row[1]
		elif any("Open Reel" in s for s in row): #if the rawCaptureName is of an open reel
			#having the format isn't enough, we need the channel configuration for open reels
			sqlstr = '''select Audio_Originals.Tape_Number, Audio_Originals.Tape_Format 
						from Audio_Originals inner join Audio_Masters on Audio_Originals.Original_Key=Audio_Masters.Original_Key 
						where Audio_Masters.rawCaptureName_''' + face + "='" + args.rawcapNumber + "' or Audio_Masters.rawCaptureName_" + face + "='" + args.rawcapNumber + ".wav'"
			row = queryFM_single(sqlstr,cnxn)
			if row:
				nameFormat["channelConfig"] = row[1]
		return nameFormat
	else:
		return None
'''
get_ff_processes returns the faces/ processes that need to be enacted on an audiofile prior to ingest
it's the result of the form that digi techs fill out when digitizing a tape
'''
def get_ff_processes(args,cnxn):
	#gets faces/ processes from filemaker form filled out by digi techs
	processes = ['delface','hlvface','dblface','revface'] #list of processes
	ffproc = {}
	sqlstr = '''select 
				deleting_''' + args.face + ",halving_" + args.face + ",doubling_" + args.face + ",reversing_" + args.face + ''' 
				from Audio_Masters 
				where rawCaptureName_''' + args.face + "='" + args.rawcapNumber + """'
				or Audio_Masters.rawCaptureName_""" + args.face + "='" + args.rawcapNumber + ".wav'"
	result = queryFM_single(sqlstr,cnxn) #use makemetadata to ask filemaker for this info
	if result is not None:
		for index,r in enumerate(result):
			if r == 'None':
				r = None #transform fm output of string "None" to python type None
			ffproc[processes[index]] = r
	return ffproc		
		
'''
get_cylinder_ID3 takes a db connection and argument for the cylinder number (no prefix) and returns a raw list of Title, Performer, Label, and date
'''
def get_cylinder_ID3(cnxn,**kwargs):
	args = ut.dotdict(kwargs)
	cnxn = pyodbc.connect(cnxn)
	sqlstr = """select Title, Performer, Composer, Label_Cat, yr
				from Cylinders
				where Call_Number_asText='""" + args.cylNumber + "'"
	print sqlstr
	row = queryFM_single(sqlstr,cnxn)
	return row

def get_tape_ID3(cnxn,**kwargs):
	args = ut.dotdict(kwargs)
	cnxn = pyodbc.connect(cnxn)
	sqlstr = """select Tape_Title, Collection_Name, Original_Recording_Date
				from Audio_Originals
				where Original_Tape_Number like '""" + args.aNumber.upper() + "%'"
	row = queryFM_single(sqlstr,cnxn)	
	return row

'''
id3Check takes an input file and verifies if there is ID3 metadata already in there
'''	
def check_ID3():
	#basically copy lines 27-50 of makemp3
	return
	
'''
makeID3fromCatalogSoup takes a bs4 soup object and returns 1 or 2 lists of ID3 tags based on the MARC xml in Alma
'''	
def makeID3fromCatalogSoup(soup):
	id3list1 = {}
	id3list2 ={}
	id3list1 = ut.dotdict(id3list1)
	id3list2 = ut.dotdict(id3list2)
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
	id3list1.title = title1
	if not artist1:
		artist1 = "Artist Unavailable"
	id3list1.artist = artist1
	if not date:
		date = "Date Unavailable"
	id3list1.date = date
	if not album:
		album = "Album Unavailable"
	id3list1.album = album
	if list028ind1:
		id3list1.label = list028ind1[0]
	else:
		id3list1.label = list028ind0[0]
	if len(title2) > 0:
		if not title2:
			title2 = "Title Unavailable"
		id3list2.title = title2
		if not artist2:
			artist2 = "Artist Unavailable"
		id3list2.artist = artist2
		if not date:
			date = "Date Unavailable"
		id3list2.date = date
		if not album:
			album = "Album Unavailable"
		id3list2.album = album
		if list028ind1:
			id3list2.label = list028ind1[1]
		else:
			id3list2.label = list028ind0[0]	
	if id3list2:
		return id3list1,id3list2
	else:
		return id3list1,None
		
########################
#########END############
########################
	
if __name__ == '__main__':
    unittest.main()	