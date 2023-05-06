#!/bin/sh

if [ "$1" = "" -o ! -f $1 ]
then
    echo "Dump file not found!"
    exit 1
fi

docker-compose stop &&
docker-compose start postgres &&
sleep 5 &&

echo "Drop DB" &&
docker-compose exec -u postgres postgres dropdb postgres &&
echo "Create empty" &&
docker-compose exec -u postgres postgres createdb postgres --owner postgres &&
echo "Restore DB" &&
cat $1 | docker-compose exec -T -u postgres postgres pg_restore -d postgres &&

docker-compose stop postgres
