#!/usr/bin/env python
import pyodbc
import argparse
import ast
import sys

def query(sqlstr,cnxn):
	cursor = cnxn.cursor()
	cursor.execute(sqlstr)
	row = cursor.fetchone()
	return row

def makenameFormatList(args,cnxn):
	#returns nameFormat in list form
	#[face,aNumber(no "a"),channelConfiguration]
	###init vars###
	thingy = ["fAB","fCD"]
	row = ''
	count = 0
	###init done###
	while not row: #try to find the Tape Number and Format based on the rawCaptureName
		if count > 1: #DO THIS BETTER
			print "uh buddy this isn't in FM"
			sys.exit()
		else:
			sqlstr="select Audio_Originals.Tape_Number, Audio_Originals.Original_Recording_Format from Audio_Originals join Audio_Masters on Audio_Originals.Original_Key=Audio_Masters.Original_Key where Audio_Masters.rawCaptureName_" + thingy[count] + "='" + args.so + "' or Audio_Masters.rawCaptureName_" + thingy[count] + "='" + args.so + ".wav'"
			#OR above necessary because sometimes the rawCaptureName has a ".wav" at the end :(
			row = query(sqlstr,cnxn)
			face = thingy[count] #assign this now, if we assign at bottom of loop, count = count + 1 and it'll be the wrong index
			count = count+1
	if row: #if we get a result (which we should because we're out of the while loop)
		rowstr = str(row) #convert to string
		if "Cassette" in rowstr: #if the rawCaptureName is of a cassette tape
			rowtup = ast.literal_eval(rowstr) #turn the string into a tuple
			rtnlist = [face] #init the return list with the face
			rtnlist.append(rowtup[0]) #this is the aNumber(no "a")
			rtnlist.append(rowtup[1]) #this is the channelConfig
			return rtnlist
		elif "Open Reel" in rowstr: #if the rawCaptureName is of an open reel
			face = face.replace("'",'') #get rid of annoying punctuation
			#having the format isn't enough, we need the channel configuration for open reels
			sqlstr = "select Audio_Originals.Tape_Number, Audio_Originals.Tape_Format from Audio_Originals inner join Audio_Masters on Audio_Originals.Original_Key=Audio_Masters.Original_Key where Audio_Masters.rawCaptureName_" + face + "='" + args.so + "' or Audio_Masters.rawCaptureName_" + face + "='" + args.so + ".wav'"
			row = query(sqlstr,cnxn)
			rowstr = str(row)
			if row:
				rowtup = ast.literal_eval(rowstr)
				rtnlist = [face]
				rtnlist.append(rowtup[0])
				rtnlist.append(rowtup[1])
				return rtnlist	

def makeffstr_ftm(args,cnxn):
	###init vars###
	silencestr = " -af silenceremove=0:0:-60dB:-15:1:-60dB" #removes silence of less than -60dba that lasts longer than 15s
	face = args.f
	ffstr = ''
	hlvstr01 = ''
	dblstr01 = ''
	###init done###
	###HALFSPEED###
	hlvface = ''
	sqlstr = "select halving_" + face + " from Audio_Masters where rawCaptureName_" + face + "='" + args.so + "' or Audio_Masters.rawCaptureName_" + face + "='" + args.so + ".wav'"
	result = query(sqlstr,cnxn)
	if result is not None and result[0] is not None:
		print "is it here"
		for r in result:
			hlvface = hlvface + r
	if "fAB" in hlvface or "fCD" in hlvface:
		hlvstr01 = ',asetrate=48000'
	###HALFSPEED DONE###
	###DOUBLESPEED###
	dblface = ''
	sqlstr = "select doubling_" + face + " from Audio_Masters where rawCaptureName_" + face + "='" + args.so + "' or Audio_Masters.rawCaptureName_" + face + "='" + args.so + ".wav'"
	result = query(sqlstr,cnxn)
	if result is not None and result[0] is not None:
		for r in result:
			dblface = dblface + r
	if "fAB" in dblface or "fCD" in dblface:
		dblstr01 = ',asetrate=192000'
	###DOUBLESPEED DONE###
	###GET IT TOGETHER###
	if hlvstr01:
		ffstr = silencestr + hlvstr01
	elif dblstr01:
		ffstr = silencestr + dblstr01
	else:	
		ffstr = silencestr
	ffstr = ffstr + " -map_channel 0.0.0 -c:a pcm_s24le processed.wav"
	return ffstr
				
def makeffstr_mono(args,cnxn):#returns an ffmpeg string for processing mono files, 4-track or Half-track or Full-track
	###INIT VARS###
	face = args.f
	channel0 = "-map_channel 0.0.0"#this separates each stream into its own file
	channel1 = "-map_channel 0.0.1"
	hlvstr0=''
	hlvstr1=''
	hlvstr01=''
	dblstr0 = ''
	dblstr1 = ''
	delface = ''
	zerostr = ''
	onestr = ''
	fxstr0 = ''
	fxstr1 = ''
	###INIT DONE###
	
	###DELETE FACE###
	#we don't delete faces technically, we just don't transcode them to the new files
	sqlstr = "select deleting_" + face + " from Audio_Masters where rawCaptureName_" + face + "='" + args.so + "' or Audio_Masters.rawCaptureName_" + face + "='" + args.so + ".wav'"
	result = query(sqlstr,cnxn)
	if result is not None and result[0] is not None:
		for r in result:
			delface = delface + r
	#if we gotta delete a face, let's deselect it from our mapping from earlier
	if delface=="fA" or delface=="fC":
		channel0 = ''
	elif delface=='fB' or delface=='fD':
		channel1=''
	###END DELETE FACE###
	###HALFSPEED###
	hlvface = ''
	sqlstr = "select halving_" + face + " from Audio_Masters where rawCaptureName_" + face + "='" + args.so + "' or Audio_Masters.rawCaptureName_" + face + "='" + args.so + ".wav'"
	result = query(sqlstr,cnxn)
	if result is not None and result[0] is not None:
		for r in result:
			hlvface = hlvface + r
	elif "fA" in hlvface or "fC" in hlvface:
		hlvstr0 = ',asetrate=48000'
	elif "fB" in hlvface or "fD" in hlvface:
		hlvstr1 = ',asetrate=48000'	
	###END HALFSPEED###
	###DOUBLESPEED###
	dblface = ''
	sqlstr = "select doubling_" + face + " from Audio_Masters where rawCaptureName_" + face + "='" + args.so + "' or Audio_Masters.rawCaptureName_" + face + "='" + args.so + ".wav'"
	result = query(sqlstr,cnxn)
	if result is not None and result[0] is not None:
		for r in result:
			dblface = dblface + r
	elif "fA" in dblface or "fC" in dblface:
		dblstr0 = ',asetrate=192000'
	elif "fB" in dblface or "fD" in dblface:
		dblstr1 = ',asetrate=192000'			
	###END DOUBLESPEED###
	###GET IT TOGETHER###
	#for left channel, stream 0
	if channel0: #fails if empty, like if it needs to be deleted
		zerostr = channel0
		if hlvstr1:
			fxstr0 = fxstr0 + hlvstr0 #add the half-speed str
		elif dblstr1:
			fxstr0 = fxstr0 + dblstr0 #add the double speed str
		if fxstr0:
			zerostr = zerostr + fxstr0 + " -c:a pcm_s24le left.wav " #no matter what, this our output fmt
		else:
			zerostr = zerostr + " -c:a pcm_s24le left.wav "
	#for right channel, stream 1
	if channel1:
		onestr = channel1
		if hlvstr1:
			fxstr1 = fxstr1 + hlvstr1
		elif dblstr1:
			fxstr1 = fxstr1 + dblstr1
		if fxstr1:
			onestr = onestr + fxstr1 + " -c:a pcm_s24le right.wav "
		else:
			onestr = onestr + " -c:a pcm_s24le right.wav "
	ffstr = zerostr + onestr
	return ffstr

def makeffstr_stereo(args,cnxn):
	###INIT VARS###
	face = args.f
	hlvstr01 = ''
	dblstr01 = ''
	silencestr = " -af silenceremove=0:0:-60dB:-15:1:-60dB"
	###END INIT###
	###HALFSPEED###
	hlvface = ''
	sqlstr = "select halving_" + face + " from Audio_Masters where rawCaptureName_" + face + "='" + args.so + "' or Audio_Masters.rawCaptureName_" + face + "='" + args.so + ".wav'"
	result = query(sqlstr,cnxn)
	if result is not None and result[0] is not None:
		for r in result:
			hlvface = hlvface + r
	if "fAB" in hlvface or "fCD" in hlvface:
		hlvstr01 = ',asetrate=48000'
	###END HALFSPEED###
	#DOUBLESPEED###
	dblface = ''
	sqlstr = "select doubling_" + face + " from Audio_Masters where rawCaptureName_" + face + "='" + args.so + "' or Audio_Masters.rawCaptureName_" + face + "='" + args.so + ".wav'"
	result = query(sqlstr,cnxn)
	if result is not None and result[0] is not None:
		for r in result:
			dblface = dblface + r
	if "fAB" in dblface or "fCD" in dblface:
		dblstr01 = ',asetrate=192000'
	###END DOUBLESPEED###
	###GET IT TOGETHER###
	ffstr = silencestr + hlvstr01 + dblstr01 + " -c:a pcm_s24le processed.wav"
	return ffstr

def makebext(args,cnxn): #makes a bext string for use with BWFMetaEdit
	###INIT VARS###
	fieldlist = ["Master_Key","Tape_Title","Mss_Number","Collection_Name","Master_Key"] #fields to select in FileMaker
	x = {} #dictionary for the resulting FileMakerField:FileMakerValue pairs
	###END INIT###
	sqlstr = "select Master_Key, Tape_Title, Mss_Number, Collection_Name, Mastered from Audio_Originals where Original_Tape_Number like '" + args.so + "/%'"
	result = query(sqlstr,cnxn)
	if result is not None: #oooooooooook if we have value sin those fields
		count = 0 #init a counter
		while count < len(fieldlist): #loop the same # of times as the field list is long
			if result[count] is not None: #if there's a value in the field
				x[fieldlist[count]]=result[count] #set the FileMakerField:FileMakerValue pair according to the index
			else: #Nonetypes can't be assigned directly
				x[fieldlist[count]]="None"
			count=count+1					
		###GET IT TOGETHER###
		bextstr = "--Originator=US,CUSB,SRC --originatorReference=cusb-"+args.so+' --Description="AudioNumber:'+args.so+'; MSS Number:'+x['Mss_Number']+'; Collection:'+x['Collection_Name']+'; Tape Title:'+x['Tape_Title']+'; Master Key:'+str(x['Master_Key'])+'"'
		#^makes the actual string based on the dictionary x and values, x[FileMakerField]=FileMakerValue
	return bextstr.encode('utf-8')	

def checkotherface(args,cnxn): #checks if there are 1 or 2 captures per tape
	if args.f == "fAB":
		sqlstr = "select rawCaptureName_fCD from Audio_Masters where rawCaptureName_fAB='" + args.so + "' or rawCaptureName_fAB='" + args.so + ".wav'"
	elif args.f == "fCD":
		sqlstr = "select rawCaptureName_fAB from Audio_Masters where rawCaptureName_fCD='" + args.so + "' or rawCaptureName_fCD='" + args.so + ".wav'"
	result = query(sqlstr,cnxn)
	return result
	
def main():		
	###INIT VARS###
	parser = argparse.ArgumentParser(description="queries and returns data from our FileMaker dbs")
	parser.add_argument('-so','--startObject',dest="so",help='the audio/ video number of the asset, a1234 for tapes, 1234 for cyls')
	parser.add_argument('-t','--tape',dest="t",action='store_true',default=False,help='use Audio Originals database as source')
	parser.add_argument('-c','--cylinder',dest='c',action='store_true',default=False,help='use Cylinders database as source')
	parser.add_argument('-id3',dest="id3",action='store_true',default=False,help='generate ID3 tags for makebroadcast')
	parser.add_argument('-pi','--pre-ingest',dest='pi',action='store_true',default=False,help='for processing files after capture')
	parser.add_argument('-p','--process',dest='p',choices=["nameFormat","otherfacecheck","reverse","ffstring","bext"],help='the type of process for which you would like data')
	parser.add_argument('-f','--face',dest='f',choices=["fAB","fCD","fA","fB","fC","fD"],help="the face of the object for which you want info")
	parser.add_argument('-cc','-channelConfig',dest='cc',choices=['Cassette','1/4-inch Half Track Mono','1/4-inch 4 Track','1/4-inch Full Track Mono','1/4-inch Half Track Stereo','1/4-inch Quarter Track Stereo'],help="the channel configuration of the tape")
	args = parser.parse_args()
	args.so = args.so.replace(".wav","")
	result = ''
	rtnlist = []
	###END INIT###
	###ID3 TAGS FOR BROADCAST WAVES MP3S AND BEYOND###
	if args.id3:
		if args.t:#if it's for a tape
			cnxn = pyodbc.connect('DRIVER={FileMaker ODBC};SERVER=filemaker.library.ucsb.edu;DATABASE=Audio Originals;UID=microservices')#init connection
			fieldlist = ["Tape_Title","Collection_Name","Original_Recording_Date"] #init fieldlist for FileMaker
			for field in fieldlist:#loop through the field list
				sqlstr = "select " + field + " from Audio_Originals where Original_Tape_Number like '" + args.so + "%'" 
				result = query(sqlstr,cnxn)#<^query the db for the value in that field for that cylinder object
				rtnlist.append(result[0])#append the found value to the list of values
		elif args.c:#if it's a cylinder
			cnxn = pyodbc.connect('DRIVER={FileMaker ODBC};SERVER=filemaker.library.ucsb.edu;DATABASE=Cylinders;UID=microservices')
			fieldlist = ["Title","Performer","Composer","Label_Cat","yr"]
			for field in fieldlist:
				sqlstr = "select " + field + " from Cylinders where Call_Number_asText='" + args.so + "'"
				result = query(sqlstr,cnxn)
				rtnlist.append(result[0])
		print rtnlist
		cnxn.close()
	###END ID3###
	if args.pi:#stands for 'pre-ingest"
		if args.t:#if it's a tape
			cnxn = pyodbc.connect('DRIVER={FileMaker ODBC};SERVER=filemaker.library.ucsb.edu;DATABASE=Audio Originals;UID=microservices')
			if args.p == 'nameFormat':
				#returns nameFormat in list form
				#[face,aNumber(no "a"),channelConfiguration]
				rtnlist = makenameFormatList(args,cnxn)
				print rtnlist
			if args.p == 'otherfacecheck':
				#returns value of the other rawCaptureName_fxx in Audio_Masters
				#one of: 'fAB','fCD','None'
				otherface = checkotherface(args,cnxn)
				print otherface
			if args.p == 'ffstring':
				#returns the processing steps for the rawCapture
				#it's in the ffmpeg syntax but it isn't the full string
				#for ftm tapes
				if 'Full Track Mono' in args.cc:
					ffstr = makeffstr_ftm(args,cnxn)
				#for other mono tapes
				elif "Half Track Mono" in args.cc or "4 Track" in args.cc:
					ffstr = makeffstr_mono(args,cnxn)
				#for stereo tapes
				else:
					ffstr = makeffstr_stereo(args,cnxn)
				print ffstr
			if args.p == "reverse":
				#returns the face(s) that need to be reversed
				###INIT###
				face = args.f
				revface = ''
				###END INIT###
				sqlstr = "select reversing_" + face + " from Audio_Masters where rawCaptureName_" + face + "='" + args.so + "' or Audio_Masters.rawCaptureName_" + face + "='" + args.so + ".wav'"
				result = query(sqlstr,cnxn)
				###GET IT TOGETHER###
				if result is not None and result[0] is not None:
					for r in result:
						revface = revface + r
				print revface
			if args.p == "bext":
				#returns bext string based on FileMaker data
				#in form that BWFMetaEdit understands but not the full string
				bextstr = makebext(args,cnxn)
				print bextstr
			cnxn.close()
main()