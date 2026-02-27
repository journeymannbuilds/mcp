"""Databricks connection using OAuth service principal (M2M)."""

import os

from databricks.sdk.core import Config, oauth_service_principal
from databricks.sql import connect


def _credential_provider():
    """Return an OAuth credential provider for service principal auth."""
    config = Config(
        host=os.environ["DATABRICKS_HOST"],
        client_id=os.environ["DATABRICKS_CLIENT_ID"],
        client_secret=os.environ["DATABRICKS_CLIENT_SECRET"],
    )
    return oauth_service_principal(config)


def get_connection():
    """Create a Databricks SQL connection using OAuth service principal credentials."""
    return connect(
        server_hostname=os.environ["DATABRICKS_HOST"],
        http_path=os.environ["DATABRICKS_HTTP_PATH"],
        credentials_provider=_credential_provider,
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
