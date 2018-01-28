#!/bin/bash
nohup /home/fairfrog/FairFrog/Code/Twitter/stream_heelhollandfair.py &> /home/fairfrog/Logs/nohup.out &
stream_pid=$!
echo $stream_pid
echo "kill -15 $stream_pid" | at 23:59
