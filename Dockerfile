FROM solr:alpine

USER root

RUN apk add --no-cache \
        curl \
        libc-dev \
        libxml2 \
        libxml2-dev \
        libxslt \
        libxslt-dev \
        python3 \
        python3-dev \
        gcc \
    && pip3 install BeautifulSoup4 lxml \
    && cp /opt/solr/contrib/velocity/lib/*jar /opt/solr/server/lib/ext/ \
    && cp /opt/solr/contrib/analysis-extras/lib/morf*jar /opt/solr/server/lib/ext/ \
    && cp /opt/solr/contrib/analysis-extras/lucene-libs/lucene-analyzers-morf*jar /opt/solr/server/lib/ext/ \
    && apk del libc-dev libxml2-dev libxslt-dev python3-dev gcc
    
COPY solr/teryt /opt/solr/server/solr/mycores/teryt

COPY push-teryt-to-solr/fetch.py /opt/solr/bin/fetch.py

COPY push-teryt-to-solr/reload.sh /opt/solr/bin/reload.sh

USER $SOLR_USER
