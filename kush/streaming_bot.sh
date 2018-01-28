#!/bin/bash
source $HOME/.bashrc 
nohup $HOME/miniconda3/bin/python /home/kush/FairFrog_Code/APICode/Twitter/kush/fairfrog_stream.py &> /home/kush/Logs/nohup.out &
stream_pid=$!
echo "Will kill $stream_pid tonight at 23:30"
echo "kill -15 $stream_pid" | at 23:30
