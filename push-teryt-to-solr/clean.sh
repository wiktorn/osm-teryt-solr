#!/bin/sh

curl http://liferay.lan:8983/solr/teryt/update --data '<delete><query>*:*</query></delete>' -H 'Content-type:text/xml; charset=utf-8'
curl http://liferay.lan:8983/solr/teryt/update --data '<commit/>' -H 'Content-type:text/xml; charset=utf-8'
