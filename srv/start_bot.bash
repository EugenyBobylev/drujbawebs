#!/bin/bash

NAME="drujba_bot"
WORKDIR=/usr/prj/drujbawebs/

echo "Starting $NAME as `whoami`"
cd $WORKDIR
echo "$PWD"

source venv/bin/activate
python start_bot.py
