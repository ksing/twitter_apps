#!/bin/bash
source $HOME/.bashrc 
cd $(dirname $0)
nohup $HOME/miniconda3/bin/python fairfrog_stream.py &> /home/kush/Logs/nohup.out &
stream_pid=$!
echo "Will kill $stream_pid tonight at 23:30"
echo "kill -15 $stream_pid" | at 23:30
