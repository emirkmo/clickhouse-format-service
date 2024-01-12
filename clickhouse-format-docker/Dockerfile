# WARNING: Large docker container. You have been warned.

# We use debian because CH does not save all versions built on alpine by default
FROM debian:11-slim as downloader

# RUN apk add gzip
RUN  apt-get update \
  && apt-get install -y wget \
  && rm -rf /var/lib/apt/lists/*

ARG CLICKHOUSE_VERSION=23.11.3.23

RUN wget https://packages.clickhouse.com/tgz/stable/clickhouse-common-static-${CLICKHOUSE_VERSION}-amd64.tgz
RUN wget https://packages.clickhouse.com/tgz/stable/clickhouse-client-${CLICKHOUSE_VERSION}-amd64.tgz

FROM downloader as unarchiver

# Common
RUN gunzip clickhouse-common-static-${CLICKHOUSE_VERSION}-amd64.tgz
RUN tar -xvf clickhouse-common-static-${CLICKHOUSE_VERSION}-amd64.tar

# Client
RUN gunzip clickhouse-client-${CLICKHOUSE_VERSION}-amd64.tgz
RUN tar -xvf clickhouse-client-${CLICKHOUSE_VERSION}-amd64.tar

FROM unarchiver as installer

RUN chmod +x clickhouse-common-static-${CLICKHOUSE_VERSION}/install/doinst.sh
RUN chmod +x clickhouse-client-${CLICKHOUSE_VERSION}/install/doinst.sh

RUN clickhouse-common-static-${CLICKHOUSE_VERSION}/install/doinst.sh
RUN clickhouse-client-${CLICKHOUSE_VERSION}/install/doinst.sh

FROM installer as clickhouse-format

ENTRYPOINT [ "clickhouse-format", "--quiet", "--multiquery", "--query" ]
