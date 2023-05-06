#!/bin/sh

if [ "$1" != "" ]
then
    dump_name=$1
else
    dump_name=dump_`date +%d-%m-%Y"_"%H_%M_%S`
fi

docker-compose stop &&
docker-compose start postgres &&
sleep 5 &&

echo "Make DB backup" &&
dump_dir=`dirname $dump_name` &&
mkdir -p $dump_dir &&
docker-compose exec -T -u postgres postgres pg_dump -c -Fc postgres > $dump_name.dump &&

docker-compose stop postgres
