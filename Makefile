CLICKHOUSE_VERSION ?= 23.11.3.23

build:
	CLICKHOUSE_VERSION=${CLICKHOUSE_VERSION} docker compose up -d --build
