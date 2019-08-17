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