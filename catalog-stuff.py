import urllib2
from bs4 import BeautifulSoup
from  __builtin__ import any as b_any
import re
import string
import argparse

def handling():
	#initialize a buncha crap
	parser = argparse.ArgumentParser(description="queries the UCSB Pegasus catalog, returns id3 list for supplied sys number")
	parser.add_argument('-sys','--systemNumber',dest="sys",help='the system number of the asset')
	args = parser.parse_args()
	url = 'http://pegasus.library.ucsb.edu:5661/sba01pub?version=1.1&operation=searchRetrieve&query=rec.id=' + args.sys + '&maximumRecords=1'
	response = urllib2.urlopen(url)
	xml = response.read()
	soup = BeautifulSoup(xml,'lxml-xml')
	tag = soup.datafield
	id3list1 = []
	id3list2 =[]
	subtitle=''
	title2=''
	for sf in soup.findAll('subfield'):
		if sf.parent['tag']=='245':
			if sf['code']=='a':
				title1 = re.sub(r"[^\w\s]", '', sf.string).lstrip()
			if sf['code']=='b':
				subtitle = re.sub(r"[^\w\s]", '', sf.string).lstrip()
			if sf['code']=='c':
				#situation1 = this is the principal performer only
				artist1 = sf.string
				#situation2 = this is the principal performer. side 2 / performers
				match = ''
				match = re.search("\.\s[^\.]+\s\/",sf.string)
				if match:
					title2 = match.group()
					artist1 = sf.string.replace(title2,'')
					
					title2 = re.sub(r"[^\w\s]", '', title2).lstrip()
					artist2 = sf.string.replace(title2,'')
					match2 = ''
					match2 = re.search("\/.*",artist2)
					if match2:
						artist2 = match2.group()
						artist1 = artist1.replace(artist2[1:],'') #lop off the first character here, a "/"
						artist2 = re.sub(r"[^\w\s;]", '', artist2).lstrip()
				artist1 = re.sub(r"[^\w\s]", '', artist1).lstrip()	
		elif sf.parent['tag']=='264':
			if sf['code']=='c':
				if sf.string.startswith("["):
					date = "n.d."
				else:
					date = re.sub(r"[^\w\s]", '', sf.string).lstrip()
		elif sf.parent['tag']==	'852':
			if sf['code']=='j':
				album = sf.string.lstrip()
	if subtitle:
		title1 = title1 + subtitle
		
	id3list1.append(title1)
	id3list1.append(artist1)
	id3list1.append(date)
	id3list1.append(album)
	if len(title2) > 0:
		id3list2.append(title2)
		id3list2.append(artist2)
		id3list2.append(date)
		id3list2.append(album)
	print id3list1
	if id3list2:
		print id3list2

handling()	