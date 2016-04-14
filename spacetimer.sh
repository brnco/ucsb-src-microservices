

echo "press space bar"
elapsedtime=0
while read -d ' '
do
echo ' '
elapsedtime=`expr $(date +%M%S) - $elapsedtime`
echo $elapsedtime >> $(date +%Y%m%d).txt
elapsedtime=$(date +%M%S)
done