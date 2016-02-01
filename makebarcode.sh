#makebarcode
read -p "barcode filename: " bcdfile

function dothething {
echo
read -p "Title: " title
read -p "Barcode: " barcode

echo -en '\n' >> $bcdfile
echo "^XA" >> $bcdfile
echo "^FO050,20^ADN,18,10" >> $bcdfile
echo "^FD$title^FS" >> $bcdfile
echo "^FO050,44^ADN,18,10" >> $bcdfile
echo "^FD$barcode^FS" >> $bcdfile
echo "^FO050,70^BY1" >> $bcdfile
echo "^BCN,40,N,N,N" >> $bcdfile
echo "^FD$barcode^FS" >> $bcdfile
echo "^XZ" >> $bcdfile
echo -en '\n' >> $bcdfile

while true; do
	read -n 1 -p "do another? " yn
	case $yn in
		[Yy]* ) dothething; break;;
		[Nn]* ) exit;;
		* ) echo "please type y or n";;
	esac
done
}

dothething


