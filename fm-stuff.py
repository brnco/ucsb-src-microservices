import pyodbc
import argparse
import ast

def query(sqlstr,cnxn):
	cursor = cnxn.cursor()
	cursor.execute(sqlstr)
	row = cursor.fetchone()
	return row

def makenameFormatList(args,cnxn):
	#returns nameFormat in list form
	#[face,aNumber(no "a"),channelConfiguration]
	thingy = ["fAB","fCD"]
	row = ''
	count = 0
	while not row: #try to find the Tape Number and Format based on the rawCaptureName
		sqlstr="select Audio_Originals.Tape_Number, Audio_Originals.Original_Recording_Format from Audio_Originals join Audio_Masters on Audio_Originals.Original_Key=Audio_Masters.Original_Key where Audio_Masters.rawCaptureName_" + thingy[count] + "='" + args.so + "' or Audio_Masters.rawCaptureName_" + thingy[count] + "='" + args.so + ".wav'"
		#OR above necessary because sometimes the rawCaptureName has a ".wav" at the end :(
		row = query(sqlstr,cnxn)
		face = thingy[count] #assign this now, if we assign at bottom of loop, count = count + 1 and it'll be the wrong index
		if count > 1: #DO THIS BETTER
			print "uh buddy this isn't in FM"
			break
		else:
			count = count+1
	if row: #if we get a result (which we should because we're out of the while loop
		rowstr = str(row)
		if "Cassette" in rowstr:
			rowtup = ast.literal_eval(rowstr) #turn the string into a tuple
			rtnlist = [face] #init the return list with the face
			rtnlist.append(rowtup[0]) #this is the aNumber(no "a")
			rtnlist.append(rowtup[1]) #this is the channelConfig
			return rtnlist
		elif "Open Reel" in rowstr:
			face = face.replace("'",'')
			sqlstr = "select Audio_Originals.Tape_Number, Audio_Originals.Tape_Format from Audio_Originals inner join Audio_Masters on Audio_Originals.Original_Key=Audio_Masters.Original_Key where Audio_Masters.rawCaptureName_" + face + "='" + args.so + "' or Audio_Masters.rawCaptureName_" + face + "='" + args.so + ".wav'"
			row = query(sqlstr,cnxn)
			rowstr = str(row)
			if row:
				rowtup = ast.literal_eval(rowstr)
				rtnlist = [face]
				rtnlist.append(rowtup[0])
				rtnlist.append(rowtup[1])
				return rtnlist	
	
def makeffstr_mono(args,cnxn):
	#returns an ffmpeg string for processing mono files, 4-track or Half-track or Full-track
	face = args.f
	#this separates each stream into its own file
	channel0 = "-map_channel 0.0.0"
	channel1 = "-map_channel 0.0.1"
	hlvstr0=''
	hlvstr1=''
	hlvstr01=''
	dblstr0 = ''
	dblstr1 = ''
	delface = ''
	zerostr = ''
	onestr = ''
	silencestr = " -af silenceremove=0:0:-50dB:-10:1:-50dB"
	
	#see if we gotta delete a face
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
	
	#grip halfspeed
	hlvface = ''
	sqlstr = "select halving_" + face + " from Audio_Masters where rawCaptureName_" + face + "='" + args.so + "' or Audio_Masters.rawCaptureName_" + face + "='" + args.so + ".wav'"
	result = query(sqlstr,cnxn)
	if result is not None and result[0] is not None:
		for r in result:
			hlvface = hlvface + r
	#if "fAB" or "fCD" in hlvface:
		#hlvstr01 = ',asetrate=48000'
	elif "fA" in hlvface or "fC" in hlvface:
		hlvstr0 = ',asetrate=48000'
	elif "fB" in hlvface or "fD" in hlvface:
		hlvstr1 = ',asetrate=48000'	
	#grip dblspeed
	dblface = ''
	sqlstr = "select doubling_" + face + " from Audio_Masters where rawCaptureName_" + face + "='" + args.so + "' or Audio_Masters.rawCaptureName_" + face + "='" + args.so + ".wav'"
	result = query(sqlstr,cnxn)
	if result is not None and result[0] is not None:
		for r in result:
			dblface = dblface + r
	#if "fAB" or "fCD" in dblface:
		#dblstr01 = ',asetrate=192000'
	elif "fA" in dblface or "fC" in dblface:
		dblstr0 = ',asetrate=192000'
	elif "fB" in dblface or "fD" in dblface:
		dblstr1 = ',asetrate=192000'			
	#for left channel, stream 0
	if channel0: #if we didn't remove it from our mapping in the delete section
		zerostr = channel0 + silencestr #add the silence remove string
		if hlvstr1:
			zerostr = zerostr + hlvstr0 #add the half-speed str
		elif dblstr1:
			zerostr = zerostr + dblstr0 #add the double speed str
		zerostr = zerostr + " -acodec pcm_s24le left.wav " #no matter what, this our output fmt
	#for right channel, stream 1
	if channel1:
		onestr = channel1 + silencestr
		if hlvstr1:
			onestr = onestr + hlvstr1
		elif dblstr1:
			onestr = onestr + dblstr1
		onestr = onestr + " -acodec pcm_s24le right.wav "	
	#print ffstr
	ffstr = zerostr + onestr
	return ffstr

def makeffstr_stereo(args,cnxn):
	face = args.f
	hlvstr01 = ''
	dblstr01 = ''
	silencestr = " -af silenceremove=0:0:-50dB:-10:1:-50dB"
	#grip halfspeed
	hlvface = ''
	sqlstr = "select halving_" + face + " from Audio_Masters where rawCaptureName_" + face + "='" + args.so + "' or Audio_Masters.rawCaptureName_" + face + "='" + args.so + ".wav'"
	result = query(sqlstr,cnxn)
	if result is not None and result[0] is not None:
		for r in result:
			hlvface = hlvface + r
	if "fAB" in hlvface or "fCD" in hlvface:
		hlvstr01 = ',asetrate=48000'
	#grip dblspeed
	dblface = ''
	sqlstr = "select doubling_" + face + " from Audio_Masters where rawCaptureName_" + face + "='" + args.so + "' or Audio_Masters.rawCaptureName_" + face + "='" + args.so + ".wav'"
	result = query(sqlstr,cnxn)
	if result is not None and result[0] is not None:
		for r in result:
			dblface = dblface + r
	if "fAB" in dblface or "fCD" in dblface:
		dblstr01 = ',asetrate=192000'
	ffstr = silencestr + hlvstr01 + dblstr01 + " -acodec pcm_s24le processed.wav"
	return ffstr

def makebext(args,cnxn):
	fieldlist = ["Master_Key","Tape_Title","Mss_Number","Collection_Name","Mastered"]
	x = {}
	sqlstr = "select Master_Key, Tape_Title, Mss_Number, Collection_Name, Mastered from Audio_Originals where Original_Tape_Number like '" + args.so + "/%'"
	print sqlstr
	result = query(sqlstr,cnxn)
	if result is not None:
		count = 0
		while count < len(fieldlist):
			if result[count] is not None:
				x[fieldlist[count]]=result[count]
			else:
				x[fieldlist[count]]="None"
			count=count+1					
		print x
		bextstr = "--Originator=US,CUSB,SRC --originatorReference=cusb-"+args.so+' --Description="AudioNumber:'+args.so+'; MSS Number:'+x['Mss_Number']+'; Collection:'+x['Collection_Name']+': Tape Title:'+x['Tape_Title']+': Master Key:'+x['Mastered']+'"'
	return bextstr	
	
def handling():		
	#initialize a buncha crap
	parser = argparse.ArgumentParser(description="queries and returns data from our FileMaker dbs")
	parser.add_argument('-so','--startObject',dest="so",help='the audio/ video number of the asset')
	parser.add_argument('-t','--tape',dest="t",action='store_true',default=False,help='use Audio Originals database as source')
	parser.add_argument('-id3',dest="id3",action='store_true',default=False,help='generate ID3 tags for makebroadcast')
	parser.add_argument('-pi','--pre-ingest',dest='pi',action='store_true',default=False,help='for processing files after capture')
	parser.add_argument('-p','--process',dest='p',choices=["nameFormat","reverse","ffstring","bext"],help='the type of process for which you would like data')
	parser.add_argument('-f','--face',dest='f',choices=["fAB","fCD","fA","fB","fC","fD"],help="the face of the object for which you want info")
	parser.add_argument('-cc','-channelConfig',dest='cc',choices=['Cassette','1/4-inch Half Track Mono','1/4-inch 4 Track','1/4-inch Full Track Mono','1/4-inch Half Track Stereo','1/4-inch Quarter Track Stereo'],help="the channel configuration of the tape")
	args = parser.parse_args()
	result = ''
	rtnlist = []
	if args.id3:
		if args.t:
			cnxn = pyodbc.connect('DRIVER={FileMaker ODBC};SERVER=filemaker.library.ucsb.edu;DATABASE=Audio Originals;UID=microservices')
			fieldlist = ["Tape_Title","Collection_Name","Original_Recording_Date"]
			for field in fieldlist:
				sqlstr = "select " + field + " from Audio_Originals where Original_Tape_Number like '" + args.so + "%'"
				result = query(sqlstr,cnxn)
				rtnList.append(result[0])
		print rtnList		
	if args.pi:
		if args.t:
			cnxn = pyodbc.connect('DRIVER={FileMaker ODBC};SERVER=filemaker.library.ucsb.edu;DATABASE=Audio Originals;UID=microservices')
			if args.p == 'nameFormat':
				#returns nameFormat in list form
				#[face,aNumber(no "a"),channelConfiguration]
				rtnlist = makenameFormatList(args,cnxn)
				print rtnlist
			if args.p == 'ffstring':
				#if it's a mono tape, run it thru this func
				if 'Full Track Mono' in args.cc:
					ffstr = silencestr + " -ac 1 -acodec pcm_s24le processed.wav"
					print ffstr
				elif "Mono" in args.cc or "4 Track" in args.cc:
					ffstr = makeffstr_mono(args,cnxn)
					print ffstr
				else:
					ffstr = makeffstr_stereo(args,cnxn)
					print ffstr
			if args.p == "reverse":
				revface = ''
				sqlstr = "select reversing_" + face + " from Audio_Masters where rawCaptureName_" + face + "='" + args.so + "' or Audio_Masters.rawCaptureName_" + face + "='" + args.so + ".wav'"
				result = query(sqlstr,cnxn)
				if result is not None and result[0] is not None:
					for r in result:
						revface = revface + r
				print revface
			if args.p == "bext":
				bextstr = makebext(args,cnxn)
				print bextstr
			cnxn.close()
handling()