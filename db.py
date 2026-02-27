"""Databricks connection using OAuth service principal (M2M)."""

import os

from databricks.sdk.core import Config, credential_provider
from databricks.sql import connect


def get_connection():
    """Create a Databricks SQL connection using OAuth service principal credentials."""
    cfg = Config(
        host=os.environ["DATABRICKS_HOST"],
        client_id=os.environ["DATABRICKS_CLIENT_ID"],
        client_secret=os.environ["DATABRICKS_CLIENT_SECRET"],
    )

    return connect(
        server_hostname=cfg.host,
        http_path=os.environ["DATABRICKS_HTTP_PATH"],
        credentials_provider=credential_provider(cfg),
    )


def execute_query(sql: str):
    """Execute a read-only SQL query and return results as list of dicts."""
    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute(sql)
        columns = [desc[0] for desc in cursor.description]
        rows = cursor.fetchall()
        return [dict(zip(columns, row)) for row in rows]
    finally:
        conn.close()
