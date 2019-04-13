#!/usr/bin/env sh

set -e

VERSION=`date '+%Y.%m.%d'`

rm -rf target
mvn dependency:copy-dependencies

docker build -t osm-teryt-solr .

if [ ! -f push-teryt-to-solr/terc.json ] ; then
    # create terc.json
    (
        cd push-teryt-to-solr
        python3 -m venv venv
        venv/bin/pip install -r requirements.txt
        venv/bin/python fetch.py
        rm -rf venv
    )
fi
docker stop my_solr || echo -n
docker rm my_solr || echo -n
docker run --name my_solr -d -p 8983:8983 -t osm-teryt-solr

sleep 5

curl 'http://localhost:8983/solr/teryt/update?commit=true' --data-binary @push-teryt-to-solr/terc.json \
    -H 'Content-type:application/json'

docker stop my_solr
docker cp security.json my_solr:/opt/mysolrhome
docker commit my_solr osm-teryt-solr:${VERSION}
docker rm my_solr
gcloud auth configure-docker
docker tag osm-teryt-solr:${VERSION} eu.gcr.io/osm-vink/osm-teryt-solr:${VERSION}
docker push eu.gcr.io/osm-vink/osm-teryt-solr:${VERSION}

