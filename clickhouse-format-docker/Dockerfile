# WARNING: Large docker container. You have been warned.
# We use debian because CH does not save all versions built on alpine by default
FROM debian:11-slim as downloader

ARG CLICKHOUSE_VERSION=23.11.3.23

# RUN apk add gzip
RUN  apt-get update \
  && apt-get install -y wget \
  && rm -rf /var/lib/apt/lists/* && apt-get purge -y --auto-remove \
  && rm -rf /etc/apt/sources.list.d/temp.list

RUN wget https://packages.clickhouse.com/tgz/stable/clickhouse-common-static-${CLICKHOUSE_VERSION}-amd64.tgz

FROM downloader as unarchiver

# Common
RUN gunzip clickhouse-common-static-${CLICKHOUSE_VERSION}-amd64.tgz
RUN tar -xvf clickhouse-common-static-${CLICKHOUSE_VERSION}-amd64.tar
RUN rm -rf clickhouse-common-static-${CLICKHOUSE_VERSION}-amd64.tar

# Just use binary instead of installing
FROM unarchiver as installer
RUN chmod +x clickhouse-common-static-${CLICKHOUSE_VERSION}/usr/bin/clickhouse

FROM installer as clickhouse-format
ENTRYPOINT [ "clickhouse", "format", "--quiet", "--multiquery", "--query" ]
