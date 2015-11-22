#!/bin/bash
# Horrible script
# will kill kodi when it's thread are < 8
# because it the number of threads hanging 
# when you try to quit after seeing a movie
# and letting the process hang

LD_LIBRARY_PATH="/usr/lib/mysql" /usr/lib/kodi/kodi.bin --standalone -fs -n &
pid=$!

sleep 5

running=1
while [[ "$running" == "1" ]]; do
        sleep 3
        nbThread=`cat /proc/$pid/status | grep Threads: | cut -d":" -f2 | tr -d '[[:space:]]'`
        if [[ "$nbThread" -lt "8" ]];then
                kill -9 $pid
                running=0
        fi
done
echo "exiting"
