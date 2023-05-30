#!/bin/bash

NAME="drujba"
WORKDIR=/usr/prj/drujbawebs/

echo "Starting $NAME as `whoami`"
cd $WORKDIR
echo "$PWD"

source venv/bin/activate
uvicorn backend.api:app --forwarded-allow-ips='*' --uds /tmp/uvicorn.sock
