import uvicorn

def main() -> None:
    """Entrypoint of the application."""
    uvicorn.run(
        "clickhouse_format_service.api:app",
        workers=2,
        host="0.0.0.0",
        port=8080,
    )


if __name__ == "__main__":
    main()