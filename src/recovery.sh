#!/bin/bash
#echo RECOVERY SCRIPT STARTED

process_cnt=$(ps -ef | grep -v 'recovery\|grep' | grep -c "$1")
echo $process_cnt

if ((process_cnt < 1))
then
  cd /home/listats/listats/src	
  nohup $1 &
  echo RECOVERED $1 at $(date)
else echo ALL GOOD
fi	
