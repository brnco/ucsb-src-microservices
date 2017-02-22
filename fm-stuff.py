import pyodbc
import argparse

def query(sqlstr):
	cnxn = pyodbc.connect('DRIVER={FileMaker ODBC};SERVER=filemaker.library.ucsb.edu;DATABASE=Audio Originals;UID=microservices')
	cursor = cnxn.cursor()
	cursor.execute(sqlstr)
	row = cursor.fetchone()
	return row

def handling():		
	#initialize a buncha crap
	parser = argparse.ArgumentParser(description="Makes a broadcast-ready file from a single input file")
	parser.add_argument('-so','--startObject',dest="so",help='the audio/ video number of the asset')
	parser.add_argument('-t','--tape',dest="t",action='store_true',default=False,help='use Audio Originals database as source')
	parser.add_argument('-id3',dest="id3",action='store_true',default=False,help='generate ID3 tags for makebroadcast')
	parser.add_argument('-bext',dest="bext",action='store_true',default=False,help="generate BEXT string for BWFMetaEdit")
	args = parser.parse_args()
	rtnList = []
	if args.id3:
		fieldlist = ["Tape_Title","Collection_Name","Original_Recording_Date"]
		for field in fieldlist:
			sqlstr = "select " + field + " from Audio_Originals where Original_Tape_Number like '" + args.so + "%'"
			result = query(sqlstr)
			rtnList.append(result[0])
	print rtnList
	
handling()