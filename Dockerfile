FROM solr:7-alpine

COPY etc/jetty.xml /opt/solr/server/etc/jetty.xml
COPY solr /opt/mysolrhome
USER root
RUN chown -R solr /opt/mysolrhome
USER solr
COPY gcp-set-port.sh /docker-entrypoint-initdb.d/
ENV SOLR_HOME=/opt/mysolrhome
