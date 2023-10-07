#!/bin/bash
#echo RECOVERY SCRIPT STARTED

process_cnt=$(ps -ef | grep -v 'recovery\|grep' | grep -c "$1")
#echo $process_cnt

if ((process_cnt < 1))
then
  cd /home/listats/listats/src
  nohup $1 &
  echo RECOVERED $1 at $(date) >> recovery.log
#else echo ALL GOOD
fi


## CRON EXAMPLES
#*/5 * * * *     /home/listats/listats/src/recovery.sh 'python3 listats-ui.py torpedo 5003'
#*/5 * * * *     /home/listats/listats/src/recovery.sh 'python3 listats-ui.py ecosystem 5004'
