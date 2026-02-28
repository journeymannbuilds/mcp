"""Databricks MCP Server — exposes list_tables, describe_table, and query tools."""

import re

from dotenv import load_dotenv
from mcp.server.fastmcp import FastMCP

from db import execute_query

load_dotenv()

mcp = FastMCP("databricks")

WRITE_PATTERN = re.compile(
    r"\b(INSERT|UPDATE|DELETE|DROP|ALTER|CREATE|TRUNCATE|MERGE|REPLACE|GRANT|REVOKE)\b",
    re.IGNORECASE,
)

SKYSCANNER_CATALOG = "skyscanner"


@mcp.tool()
def list_tables(catalog: str = "longtail") -> list[dict]:
    """List all fully-qualified table names in a catalog."""
    sql = f"SHOW TABLES IN {catalog}"
    rows = execute_query(sql)
    return rows


@mcp.tool()
def describe_table(table: str) -> list[dict]:
    """Describe columns of a fully-qualified table (catalog.schema.table)."""
    sql = f"DESCRIBE TABLE {table}"
    return execute_query(sql)


@mcp.tool()
def query(sql: str) -> list[dict]:
    """Execute a read-only SQL query against Databricks.

    Write operations are blocked. Queries against Skyscanner tables must include
    a filter on the `dt` column for partition pruning.
    """
    if WRITE_PATTERN.search(sql):
        raise ValueError("Write operations are not allowed. This server is read-only.")

    if SKYSCANNER_CATALOG in sql.lower() and "dt" not in sql.lower():
        raise ValueError(
            "Queries on Skyscanner tables must filter on the `dt` column for partition pruning."
        )

    return execute_query(sql)


if __name__ == "__main__":
    mcp.run(transport="stdio")
