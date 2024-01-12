# Clickhouse Format via Docker

`clickhouse-format` is a program built into clickhouse for checking
format of SQL queries.

In this dockerfile, we build a slim debian image with clickhouse installed
using the version matching the one from production. The container then runs
`clickhouse-format` with the following arguments:

```Bash
clickhouse-format --quiet --multiquery --query "<SQL QUERY>"
```

Where the SQL query is provided at runtime via `docker run`, and `--quiet` and
`--multiquery` are settings.

## Usage

Build and run it against sql you want to test for clickhouse formatting.

Usecases:

- pre-commit hook for checking clickhouse sql.
- When using with dbt, check compiled clickhouse sql.
- In general, checking generated or user-written SQL for clickhouse in CI
without building clickhouse in CI, which is very heavy.

```Bash
# Either build with docker build or use the makefile
# Docker build
docker build -t docker-clickhouse-format:latest .
# Makefile
make build

# Run with text query
docker run --rm -i -t docker-clickhouse-format:latest "SQL TO QUERY;"

# Run with query from file:
# Assuming pinned_devices.sql
docker run --rm -i -t docker-clickhouse-format:latest \
"$(<my/file/path/filename.sql)"
```

If you get no output, you are good to go. Invalid SQL will raise clickhouse errors.
Go ahead and try it yourself!

Official clickhouse docs:
[clickhouse-format](https://clickhouse.com/docs/en/operations/utilities/clickhouse-format)
