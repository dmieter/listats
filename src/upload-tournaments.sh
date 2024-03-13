#!/bin/bash
cd /home/listats/listats/src
echo $1 $2 >> upload.log
python3 listats_upload.py $1 $2 >> upload.log 2>> upload.log
