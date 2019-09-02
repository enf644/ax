#!/bin/bash

process=$1
PID_FILE="/home/wineuser/.local/lib/python3.6/site-packages/ax/ax.pid"
case $process in
    start)
        echo "STARTING Ax server in port 8080"
        python3 /home/wineuser/.local/lib/python3.6/site-packages/ax/main.py --host=10.128.0.34 --port=8080 &
        echo $! > $PID_FILE
        ;;

    stop)
        kill -9 $(cat $PID_FILE)
        rm $PID_FILE
        ;;

    *)
        echo "INVALID OPTION"
        ;;
esac


# sudo nano /etc/monit/monitrc
# sudo monit status
# sudo monit reload
# sudo nano /var/log/monit.log


#   check host ax with address 84.201.174.246
#     start program = "/home/wineuser/.local/lib/python3.6/site-packages/ax/ax.sh start"
#     stop program = "/home/wineuser/.local/lib/python3.6/site-packages/ax/ax.sh stop"
#     if failed port 8080 protocol http
#        and request /deck
#     then restart