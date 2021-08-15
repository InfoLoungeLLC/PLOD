#!/bin/bash 
csv="memory_result/memory_case_"$1"_datacount_"$2".csv"
rm $csv
touch $csv
echo "writing to memory.csv"
echo "TIME_STAMP,Java Memory Usage (MB)" | tee -a $csv
total="$(free -m | grep Mem | tr -s ' ' | cut -d ' ' -f 2)"
echo $total
sleep 1

while true
do
    DATE=`date +"%H:%M:%S:%s%:z"`
    echo -n "$DATE, " | tee -a $csv
    var="$(top -b -n 1| grep -w java | tr -s ' ' | cut -d ' ' -f 10)"
    monitor=`top -b -n 1| grep -w java | tr -s ' ' | cut -d ' ' -f 10`
    echo $monitor
    if [[ `echo "$monitor > 0" | bc` == 1 ]]; then
        echo "scale=3; ($var*$total/100)" | bc | tee -a $csv
    else
        break
    fi
    sleep 5
done