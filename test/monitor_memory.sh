#!/bin/bash 
rm memory.csv
touch memory.csv
echo "writing to memory.csv"
echo "TIME_STAMP,Java Memory Usage (MB)" | tee -a memory.csv
total="$(free -m | grep Mem | tr -s ' ' | cut -d ' ' -f 2)"
echo $total


while true
do
    DATE=`date +"%H:%M:%S:%s%:z"`
    echo -n "$DATE, " | tee -a memory.csv   
    var="$(top -b -n 1| grep -w java | tr -s ' ' | cut -d ' ' -f 11) "
    monitor=`top -b -n 1| grep -w java | tr -s ' ' | cut -d ' ' -f 11`
    echo $monitor
    if [[ `echo "$monitor > 0" | bc` == 1 ]]; then
        echo "scale=3; ($var*$total/100)" | bc | tee -a memory.csv
    else
        break
    fi
    sleep 1
done