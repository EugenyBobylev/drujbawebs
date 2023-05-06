#!/bin/sh

docker-compose stop &&
docker-compose start postgres &&
sleep 5 &&

echo "Drop DB" &&
docker-compose exec -u postgres postgres dropdb postgres &&

docker-compose stop postgres
