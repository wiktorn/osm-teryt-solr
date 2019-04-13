FROM solr:7-alpine

COPY solr /opt/mysolrhome
USER root
RUN chown -R solr /opt/mysolrhome
USER solr
COPY target/dependency /opt/mysolrhome/lib
COPY gcp-set-port.sh /docker-entrypoint-initdb.d/
ENV SOLR_HOME=/opt/mysolrhome
