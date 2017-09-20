#!/usr/bin/env python
#makebarcodes
#uses the CLI to make barcodes for discs
#prints a text file that can be read by Zebra barcode printers

import os
import shutil
import time
import sys
import argparse
###UCSB modules###
import config as rawconfig
import util as ut
import logger as log
import mtd
import makestartobject as makeso

def makebarcodefile ():
	parser = argparse.ArgumentParser(description="makes a barcode.bcd file on Desktop that can be sent to Zebra barcode printer")
	args = parser.parse_args()
	#initialize a barcode file in the current directory
	try:
		tmpBcdFile = os.path.join(os.environ["HOME"], "Desktop", 'temp-bcd-' + str(time.time()) + '.txt')
	except:
		tmpBcdFile = os.path.join(os.environ["USERPROFILE"], "Desktop", 'temp-bcd-' + str(time.time()) + '.txt')
	if not tmpBcdFile:
		print "could initialize barcode file for Mac at:"
		print os.path.join(os.environ["HOME"], "Desktop", 'temp-bcd-' + str(time.time()) + '.txt')
		print "or for Windows at:"
		print os.path.join(os.environ["USERPROFILE"], "Desktop", 'temp-bcd-' + str(time.time()) + '.txt')
		sys.exit()				
	while True: #loops as long as the user answers yes
		bcdf = open(tmpBcdFile, 'a') #open the text file
		title = raw_input("Title: ") #grab the title from the user input on the CLI
		barcode = raw_input("Barcode: ") #grab the barcode from the user input on the CLI
		#lol
		if len(barcode) > 30:
			print "Error: barcode must be 30 characters or fewer, please redo"
		#this is the text string that the barcode printer understands
		lol = ['\n','^XA','\n','^FO050,20^ADN,18,10','\n','^FD' + title + '^FS','\n','^FO050,44^ADN,18,10','\n','^FD' + barcode + '^FS','\n','^FO050,70^BY1','\n','^BCN,40,N,N,N','\n','^FD' + barcode + '^FS','\n','^XZ','\n','\n']
		bcdf.writelines(lol) #write the List of Lines (lol) to the txt file
		bcdf.close() #housekeeping
		contd = raw_input("Do another (y/n)? ") #ask the user if they wanna continue
		while contd.lower() not in ('y','n'): #do some error checking
			contd = raw_input("Buddy, just type y or n if do or don't wanna do another")
		if contd == 'n': #if they answer no, they don't wanna continue, break the loop
			break
	outputPlace(tmpBcdFile) #save it somewhere
	return 

def outputPlace(tmpBcdFile): #saves the output barcode file somewhere
	print "Your file is currently saved here: " + tmpBcdFile
	moveYN = raw_input("Would you like to save it somewhere else (Y/N)? ")
	moveYN = moveYN.lower()
	if moveYN == 'y':
		whereto = raw_input("Where would you like to save it (full path to folder plz)? ") #ask them where to move it to
		whereto = whereto.replace("\\","/") #for windows peeps
		if not os.path.exists(whereto):
			os.makedirs(whereto) #recursively make the dirs necessary to move it
		shutil.move(tmpBcdFile,whereto) #move it
	elif moveYN == 'n':
		print "Okie Dokie" #fine, i mean i guess, whatever
	else: #error checking
		print "Buddy, you gotta type Y or N"
		outputPlace()
	return

if __name__ == '__main__':
	makebarcodefile()