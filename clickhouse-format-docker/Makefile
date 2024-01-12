APPLICATION_NAME ?= clickhouse-format-docker
CLICKHOUSE_VERSION ?= 23.11.3.23

build:
	docker build --build-arg CLICKHOUSE_VERSION=${CLICKHOUSE_VERSION} --tag "${APPLICATION_NAME}:${CLICKHOUSE_VERSION}" .
# Tagging with latest to ensure ci always uses latest version even if multiple versions are built
	docker tag "${APPLICATION_NAME}:${CLICKHOUSE_VERSION}" "${APPLICATION_NAME}:latest"
