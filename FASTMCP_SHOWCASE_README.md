# FastMCP Components Showcase

A comprehensive demonstration of all FastMCP 2.x core components.

## Quick Start

```bash
# Install dependencies
pip install "fastmcp>=2.14.0" fastapi uvicorn pydantic aiohttp

# Run in different modes:
python fastmcp_showcase.py              # stdio mode (for Claude Desktop)
python fastmcp_showcase.py --http       # HTTP server mode
python fastmcp_showcase.py --fastapi    # FastAPI integration mode
```

## Running Modes

| Mode | Command | Use Case |
|------|---------|----------|
| stdio | `python fastmcp_showcase.py` | Claude Desktop integration |
| HTTP | `python fastmcp_showcase.py --http --port 8000` | Remote MCP access |
| FastAPI | `python fastmcp_showcase.py --fastapi --port 8000` | REST API + MCP combined |

## Showcased Components

### 1. Tools (9 examples)
- **Simple sync/async**: `add_numbers`, `multiply_numbers`
- **Pydantic models**: `create_user` with `UserProfile` input validation
- **Enum parameters**: `create_task` with `Priority` and `TaskStatus`
- **Annotated validation**: `calculate_discount` with Field constraints
- **Custom metadata**: `advanced_search` with name, description, tags
- **Context usage**: `process_data_with_context` (logging, progress)
- **Resource access**: `analyze_config_with_context` (ctx.read_resource)
- **Multiple return types**: `get_sample_data` (dict, str, Pydantic)

### 2. Resources (6 examples)
- **Static**: `config://version`, `config://settings`
- **Dynamic templates**: `user://{user_id}/profile`
- **Multi-parameter**: `data://{category}/{item_id}`
- **Async resource**: `api://{endpoint}/status`
- **Typed parameters**: `metrics://{service}/last/{count}`

### 3. Prompts (4 examples)
- **Simple**: `greeting_prompt`
- **Multi-parameter**: `code_review_prompt`
- **Custom metadata**: `data_analysis_request`
- **Structured messages**: `conversation_starter_prompt`

### 4. Server Composition
- Sub-servers: `math_server`, `string_server`
- `import_server()` with prefix for static composition
- All sub-server tools/resources available with prefix (e.g., `math_add`)

### 5. FastAPI Integration
- Mount MCP at `/mcp` endpoint
- REST wrappers at `/api/tools`, `/api/resources`, `/api/prompts`
- Health check at `/health`
- OpenAPI docs at `/docs`

## Claude Desktop Configuration

Add to `claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "fastmcp-showcase": {
      "command": "python",
      "args": ["/path/to/fastmcp_showcase.py"]
    }
  }
}
```

## API Endpoints (FastAPI Mode)

| Endpoint | Description |
|----------|-------------|
| `GET /` | API info |
| `GET /health` | Health check |
| `GET /api/tools` | List MCP tools |
| `GET /api/resources` | List MCP resources |
| `GET /api/prompts` | List MCP prompts |
| `/mcp/*` | MCP protocol endpoint |

## References

- [FastMCP Documentation](https://gofastmcp.com/getting-started/welcome)
- [FastMCP GitHub](https://github.com/jlowin/fastmcp)
- [FastAPI Integration](https://gofastmcp.com/integrations/fastapi)
- [MCP Protocol](https://modelcontextprotocol.io)
