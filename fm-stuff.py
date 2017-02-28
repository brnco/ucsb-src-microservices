import pyodbc
import argparse
import ast

def query(sqlstr,cnxn):
	cursor = cnxn.cursor()
	cursor.execute(sqlstr)
	row = cursor.fetchone()
	print row
	return row

def handling():		
	#initialize a buncha crap
	parser = argparse.ArgumentParser(description="queries and returns data from our FileMaker dbs")
	parser.add_argument('-so','--startObject',dest="so",help='the audio/ video number of the asset')
	parser.add_argument('-t','--tape',dest="t",action='store_true',default=False,help='use Audio Originals database as source')
	parser.add_argument('-id3',dest="id3",action='store_true',default=False,help='generate ID3 tags for makebroadcast')
	parser.add_argument('-pi','--pre-ingest',dest='pi',action='store_true',default=False,help='for processing files after capture')
	parser.add_argument('-p','--process',dest='p',choices=["nameFormat","reverse","ffstring","ch","deck"],help='the type of process for which you would like data')
	parser.add_argument('-f','--face',dest='f',choices=["fAB","fCD","fA","fB","fC","fD"],help="the face of the object for which you want info")
	parser.add_argument('-cc','-channelConfig',dest='cc',choices=['1/4-inch Half Track Mono','1/4-inch 4 Track','1/4-inch Full Track Mono','1/4-inch Half Track Stereo','1/4-inch Quarter Track Stereo'],help="the channel configuration of the tape")
	parser.add_argument('-bext',dest="bext",action='store_true',default=False,help="generate BEXT string for BWFMetaEdit")
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
				sqlstr = "select Audio_Originals.Tape_Number, Audio_Originals.Tape_Format from Audio_Originals inner join Audio_Masters on Audio_Originals.Original_Key=Audio_Masters.Original_Key where Audio_Masters.rawCaptureName_fAB='" + args.so + "'"
				result = query(sqlstr,cnxn)
				if result:
					rtnlist.append("fAB")
					for r in result:
						rtnlist.append(r)
				if not result:
					sqlstr = "select Audio_Originals.Tape_Number, Audio_Originals.Tape_Format from Audio_Originals inner join Audio_Masters on Audio_Originals.Original_Key=Audio_Masters.Original_Key where Audio_Masters.rawCaptureName_fCD='" + args.so + "'"
					result = query(sqlstr,cnxn)
					if result:
						rtnlist.append("fCD")
					for r in result:
						rtnlist.append(r)
			if args.p == 'ffstring':
				sqlstr = "select * from Audio_Masters where rawCaptureName_fAB='01234'"
				result= query(sqlstr,cnxn)
				print result
				foo = raw_input("eh")
				face = args.f
				if len(face) > 2:
					if face=="fA" or face=="fB":
						rcFace="fAB"
					elif face=="fC" or face=="fD":
						rcFace="fCD"
					else:
						rcFace = face
				#grip delete
				if "Mono" in args.cc or "4 Track" in args.cc:
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
					if face == "fAB":
						sqlstr = "select del_fA, del_fB from Audio_Masters where rawCaptureName_" + rcFace + "='" + args.so + "'"
					else:
						sqlstr = "select del_fC, del_fD from Audio_Masters where rawCaptureName_" + rcFace + "='" + args.so + "'"
					#print sqlstr
					result = query(sqlstr,cnxn)
					#print result
					#foo=raw_input("eh")
					for r in result:
						if r is not None:
							delface = delface + r
					if delface=="del_fA" or delface=="del_fC":
						channel0 = ''
					elif delface=='del_fB' or delface=='del_fD':
						channel1=''
					#grip reverse
					'''revface = ''
					sqlstr = "select reverse_" + face + " from Audio_Masters where rawCaptureName_" + rcFace + "='" + args.so + "'"
					result = query(sqlstr,cnxn)
					for r in result:
						if r is not None:
							revface = r'''
					#grip halfspeed
					hlvface = ''
					sqlstr = "select hlvspd_" + face + " from Audio_Masters where rawCaptureName_" + rcFace + "='" + args.so + "'"
					result = query(sqlstr,cnxn)
					print result
					for r in result:
						if r is not None:
							hlvface = hlvface + r
					if "fAB" or "fCD" in hlvface:
						hlvstr01 = ',asetrate=48000'
					elif "fA" in hlvface or "fC" in hlvface:
						hlvstr0 = ',asetrate=48000'
					elif "fB" in hlvface or "fD" in hlvface:
						hlvstr1 = ',asetrate=48000'	
					#grip dblspeed
					dblface = ''
					sqlstr = "select dblspd_" + face + " from Audio_Masters where rawCaptureName_" + rcFace + "='" + args.so + "'"
					result = query(sqlstr,cnxn)
					for r in result:
						if r is not None:
							dblface = dblface + r
					if "fAB" or "fCD" in dblface:
						dblstr01 = ',asetrate=192000'
					elif "fA" in dblface or "fC" in dblface:
						dblstr0 = ',asetrate=192000'
					elif "fB" in dblface or "fD" in dblface:
						dblstr1 = ',asetrate=192000'			
					#for left channel, stream 0
					if channel0:
						zerostr = channel0 + silencestr
						if hlvstr1:
							zerostr = zerostr + hlvstr0
						elif dblstr1:
							zerostr = zerostr + dblstr0
						zerostr = zerostr + " -acodec pcm_s24le left.wav "
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
					print ffstr
					foo=raw_input("eh")
				'''
				avlab-audio gives face, raw name, aNumber, channel config
				with that info:
					1. map channels
					2. query for delete
					3. query for half-speed
					4. query for double-speed
					
				
				
			
			print rtnlist'''
	
	
handling()