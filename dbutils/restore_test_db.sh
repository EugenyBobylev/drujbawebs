#!/bin/sh

if [ "$1" = "" -o ! -f $1 ]
then
    echo "Dump file not found!"
    exit 1
fi

docker-compose stop postgres &&
docker-compose start postgres &&
sleep 5 &&

echo "Drop DB" &&
docker-compose exec -u postgres postgres dropdb test_db &&
echo "Create empty" &&
docker-compose exec -u postgres postgres createdb test_db --owner postgres &&
echo "Restore DB" &&
cat $1 | docker-compose exec -T -u postgres postgres pg_restore -d test_db &&

docker-compose restart
