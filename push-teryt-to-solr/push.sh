#!/bin/sh

curl 'http://liferay.lan:8983/solr/teryt/update?commit=true' --data-binary @terc.json -H 'Content-type:application/json'
