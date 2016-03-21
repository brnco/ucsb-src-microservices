import os
import shutil
import time


tmpBcdFile = os.getcwd() + '/temp-bcd-' + str(time.time()) + '.txt'

def makebarcodefile ():
	while True:
		bcdf = open(tmpBcdFile, 'a')
		title = raw_input("Title: ")
		barcode = raw_input("Barcode: ")
		lol = ['\n','^XA','\n','^FO050,20^ADN,18,10','\n','^FD' + title + '^FS','\n','^FO050,44^ADN,18,10','\n','^FD' + barcode + '^FS','\n','^FO050,70^BY1','\n','^BCN,40,N,N,N','\n','^FD' + barcode + '^FS','\n','^XZ','\n','\n']
		bcdf.writelines(lol)
		bcdf.close()
		contd = raw_input("Do another (y/n)? ")
		while contd.lower() not in ('y','n'):
			contd = raw_input("Buddy, just type y or n if do or don't wanna do another")
		if contd == 'n':
			break
	outputPlace()
	return

def outputPlace():
	print "Your file is currently saved here: " + tmpBcdFile
	moveYN = raw_input("Would you like to save it somewhere else (Y/N)? ")
	moveYN = moveYN.lower()
	if moveYN == 'y':
		whereto = raw_input("Where would you like to save it (full path to folder plz)? ")
		whereto = whereto.replace("\\","/")
		if not os.path.exists(whereto):
			os.makedirs(whereto)
		shutil.move(tmpBcdFile,whereto)
	elif moveYN == 'n':
		print "Okie Dokie"
	else:
		print "Buddy, you gotta type Y or N"
		outputPlace()
	return

makebarcodefile()
