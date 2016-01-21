#!/bin/sh

curl 'http://osm-teryt-solr.lan:8983/solr/teryt/update?commit=true' --data-binary @terc.json -H 'Content-type:application/json'
