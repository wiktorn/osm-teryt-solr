#!/bin/sh

BINDIR="$(dirname $(readlink -nf $0))"
# reset database
cd /tmp

curl http://localhost:8983/solr/teryt/update --data '<delete><query>*:*</query></delete>' -H 'Content-type:text/xml; charset=utf-8'
curl http://localhost:8983/solr/teryt/update --data '<commit/>' -H 'Content-type:text/xml; charset=utf-8'

python3 $BINDIR/fetch.py

curl 'http://localhost:8983/solr/teryt/update?commit=true' --data-binary @terc.json -H 'Content-type:application/json'
rm terc.json
