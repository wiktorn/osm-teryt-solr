FreeBSD:
pkg install apache-solr lucene5

(lucene5 needed for additional plugins, such as Morflogik, EdgeNGram)

From https://github.com/morfologik/morfologik-stemming build:
* morfologik-polish 
* morfologik-stemming
* morfologik-fsa

and add them to classpath (/usr/local/share/java/classes/)

From push-teryt-to-solr run:
python3.4 fetch.py
sh push.sh

(check for valid hostname in upload.sh)
