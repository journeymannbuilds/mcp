# Databricks MCP Server

A minimal MCP server that exposes Databricks SQL tools via the Model Context Protocol. Authenticates using OAuth service principal (M2M) — no PAT required.

## Tools

| Tool | Description |
|------|-------------|
| `list_tables` | List all tables in a given catalog |
| `describe_table` | Describe columns of a fully-qualified table |
| `query` | Execute a read-only SQL query |

## Setup

1. **Clone and install dependencies:**

```bash
pip install -r requirements.txt
```

2. **Configure environment variables:**

```bash
cp .env.example .env
# Fill in your Databricks workspace details and service principal credentials
```

Required variables:
- `DATABRICKS_HOST` — Databricks workspace URL
- `DATABRICKS_HTTP_PATH` — SQL warehouse HTTP path
- `DATABRICKS_CLIENT_ID` — Service principal client ID
- `DATABRICKS_CLIENT_SECRET` — Service principal client secret

3. **Run the server:**

```bash
python server.py
```

The server uses stdio transport by default for MCP communication.

## Claude Desktop Configuration

Add to your `claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "databricks": {
      "command": "python",
      "args": ["/absolute/path/to/server.py"]
    }
  }
}
```

## Constraints

- **Read-only** — write operations (INSERT, UPDATE, DELETE, DROP, etc.) are blocked.
- **Partition pruning** — queries against Skyscanner tables must include a `dt` column filter.
