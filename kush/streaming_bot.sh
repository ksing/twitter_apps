#!/bin/bash
source $HOME/.bashrc 
cd $(dirname $0)
if [[ $(ps -f -u kush | grep fairfrog_stream | wc -l) -lt 2 ]]; then
	$HOME/miniconda3/bin/python fairfrog_stream.py &
fi
