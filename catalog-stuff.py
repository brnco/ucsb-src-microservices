import urllib2
from bs4 import BeautifulSoup
from  __builtin__ import any as b_any
import re
import string
import pickle
import argparse
import lxml

def query(args):
	#use aleph api to grip the catalog record for our object
	#obsolete aleph api call
	#url = 'http://pegasus.library.ucsb.edu:5661/sba01pub?version=1.1&operation=searchRetrieve&query=rec.id=' + args.sys + '&maximumRecords=1'
	url = "https://ucsb.alma.exlibrisgroup.com/view/sru/01UCSB_INST?version=1.2&operation=searchRetrieve&schema=marcxml&query=alma.mms_tagSuppressed%3Dfalse+and+alma.mms_id%3D" + args.sys + "%29"
	response = urllib2.urlopen(url) #do that
	xml = response.read() #gives back lovely marc xml
	soup = BeautifulSoup(xml,'lxml') #soupify it for parsing
	return soup

def main():
	###INIT VARS###
	parser = argparse.ArgumentParser(description="queries the UCSB Pegasus catalog, returns id3 list for supplied sys number")
	parser.add_argument('-sys','--systemNumber',dest="sys",help='the system number of the asset')
	args = parser.parse_args()
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
	###END INIT###
	
	###GET XML SOUP FROM CATALOG
	soup = query(args)
	###END GETTING XML SOUP FROM CATALOG###
	
	###DO SOMETHING USEFUL###
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
	print id3list1
	if id3list2:
		print id3list2

main()	