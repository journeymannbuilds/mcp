"""Databricks MCP Server — exposes list_tables, describe_table, and query tools."""

import re

from dotenv import load_dotenv
from mcp.server.fastmcp import FastMCP

from db import execute_query

load_dotenv()

mcp = FastMCP(
    "databricks",
    instructions=(
        "You are connected to a Databricks SQL warehouse via this MCP server. "
        "Use the provided tools to explore and query data. Follow these rules:\n"
        "1. This server is READ-ONLY. All write operations (INSERT, UPDATE, DELETE, DROP, etc.) are blocked.\n"
        "2. Always start by calling list_tables to discover available tables before querying.\n"
        "3. Use describe_table to understand column names and types before writing queries.\n"
        "4. Queries on Skyscanner tables MUST include a filter on the `dt` column for partition pruning.\n"
        "5. Write efficient SQL — use LIMIT clauses to avoid returning excessive rows.\n"
        "6. Use fully-qualified table names: catalog.schema.table."
    ),
)

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
