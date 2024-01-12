ARG CLICKHOUSE_VERSION=23.11.3.23
# We use debian because CH does not save all versions built on alpine by default
FROM clickhouse/clickhouse-server:${CLICKHOUSE_VERSION} as ch-downloader

ENTRYPOINT [ "clickhouse", "format", "--quiet", "--multiquery", "--query" ]
