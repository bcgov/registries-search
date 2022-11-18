FROM bitnami/solr:9.0.0
USER root

ARG VCS_REF="missing"
ARG BUILD_DATE="missing"

ENV VCS_REF=${VCS_REF}
ENV BUILD_DATE=${BUILD_DATE}

LABEL org.label-schema.vcs-ref=${VCS_REF} \
    org.label-schema.build-date=${BUILD_DATE}

# Copy over solr files
COPY bitnami /bitnami
RUN rm -rf bitnami/bitnami/solr/server/solr/search/data

RUN chmod -R 777 /bitnami

USER 1001
