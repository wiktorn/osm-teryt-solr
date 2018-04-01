FreeBSD:
pkg install apache-solr lucene5

(lucene5 needed for additional plugins, such as Morflogik, EdgeNGram)

From https://github.com/morfologik/morfologik-stemming build:
* morfologik-polish 
* morfologik-stemming
* morfologik-fsa

and add them to classpath (/usr/local/share/java/classes/)

Download Apache Velocity (https://velocity.apache.org/download.cgi):
* engine
* tools

And copy:
* velocity-1.7.jar
* velocity-tools-2.0.jar
To: /usr/local/share/java/classes/

From push-teryt-to-solr run:
python3.6 -m venv venv
venv/bin/pip install -r requirements.txt
git submodule init
git submodule update --remote
python3.6 fetch.py
sh push.sh

(check for valid hostname in upload.sh)
