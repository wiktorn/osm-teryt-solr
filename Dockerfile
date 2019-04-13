FROM solr:7-alpine

COPY solr /opt/mysolrhome
COPY target/dependency /opt/mysolrhome/lib
USER root
RUN chown -R solr /opt/mysolrhome
USER solr
ENV SOLR_HOME=/opt/mysolrhome