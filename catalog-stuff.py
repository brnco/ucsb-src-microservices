import urllib2
from bs4 import BeautifulSoup
from  __builtin__ import any as b_any
import re
import string
import pickle
import argparse

def handling():
	#initialize a buncha crap
	parser = argparse.ArgumentParser(description="queries the UCSB Pegasus catalog, returns id3 list for supplied sys number")
	parser.add_argument('-sys','--systemNumber',dest="sys",help='the system number of the asset')
	args = parser.parse_args()
	#use aleph api to grip the catalog record for our object
	url = 'http://pegasus.library.ucsb.edu:5661/sba01pub?version=1.1&operation=searchRetrieve&query=rec.id=' + args.sys + '&maximumRecords=1'
	response = urllib2.urlopen(url) #do that
	xml = response.read() #gives back lovely marc xml
	soup = BeautifulSoup(xml,'lxml-xml') #soupify it for parsing
	#init our data objects
	id3list1 = []
	id3list2 =[]
	subtitle=''
	title2=''
	list028ind0=[]
	list028ind1=[]
	#ok here we go
	#step1: find out if there are two sides to this record
	for sf in soup.findAll('subfield'): #find every xml tag named subfield
		if sf.parent['tag']=='740':
			title2 = sf.string.lstrip()
	for sf in soup.findAll('subfield'):
		if sf.parent['tag']=='245': #find the subfields whose parent is the marc 245 field
			if sf['code']=='a': #marc 245 $a
				title1 = sf.string.lstrip() #assign the first title, strip non-word chars and leading spaces
			if sf['code']=='b': #marc 245 $b
				subtitle = sf.string.lstrip() #assign subtitle, strip non-word chars and leading spaces
		elif sf.parent['tag']=='511':
			match = ''
			match = re.search("by.*\(side A\)(\s|\.)",sf.string)
			if match:
				artist1 = match.group().replace("(side A)","").replace("by ","").lstrip()
			else:
				artist1=sf.string
				artist1 = re.sub(r".*by ",'',artist1)
			match = ''
			match = re.search("\(side A\).*\(side B\)",sf.string)
			if match:
				artist2 = match.group().replace("(side A) ; ","").replace("(side B)","").lstrip()
			elif len(title2) > 0:
				artist2 = artist1
				match2 = ''
				match2 = re.search(r".*;",artist2)
				if match2:
					artist2 = match2.group().replace(" ;","")
		elif sf.parent['tag']==	'852': #grip the Columbia A69 part
			if sf['code']=='j':
				album = sf.string.lstrip()
		elif sf.parent['tag']=='028':
			if sf.parent['ind1']=='0':
				if sf['code']=='a':
					list028ind0.append(sf.string)
			elif sf.parent['ind1']=='1':
				if sf['code']=='a':
					list028ind1.append(sf.string)
	for cf in soup.findAll('controlfield'):
		if cf['tag']=='008':
			date = cf.string[7:11]
	
	if subtitle:
		title1 = title1 + subtitle

	#append everything to the lists	
	id3list1.append(title1)
	id3list1.append(artist1)
	id3list1.append(date)
	id3list1.append(album)
	if list028ind1:
		id3list1.append(list028ind1[0])
	else:
		id3list1.append(list028ind0[0])
	if len(title2) > 0:
		id3list2.append(title2)
		id3list2.append(artist2)
		id3list2.append(date)
		id3list2.append(album)
		if list028ind1:
			id3list2.append(list028ind1[1])
		else:
			id3list2.append(list028ind0[0])	
	print id3list1
	if id3list2:
		print id3list2

handling()	