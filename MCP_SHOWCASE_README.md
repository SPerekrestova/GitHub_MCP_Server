# MCP Showcase Server & Generic Client

A comprehensive demonstration of building MCP (Model Context Protocol) servers with Gradio interface and a vendor-agnostic client.

## Overview

This showcase includes:

- **`mcp_showcase_server.py`**: Full-featured MCP server with Gradio UI and REST API
- **`mcp_generic_client.py`**: Generic client using standard HTTP (no vendor lock-in)

## Quick Start

### 1. Install Dependencies

```bash
# Create virtual environment (recommended)
python3 -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install required packages
pip install fastmcp gradio fastapi uvicorn httpx pydantic aiohttp
```

### 2. Start the Server

```bash
python mcp_showcase_server.py
```

The server starts with multiple interfaces:

| Interface | URL | Description |
|-----------|-----|-------------|
| Gradio UI | http://localhost:8080/ | Interactive web interface |
| MCP Endpoint | http://localhost:8080/mcp | MCP protocol (SSE transport) |
| REST API | http://localhost:8080/api/ | HTTP REST endpoints |
| API Docs | http://localhost:8080/docs | OpenAPI documentation |

### 3. Use the Client

```bash
# Run demo (shows all features)
python mcp_generic_client.py --demo

# Interactive mode
python mcp_generic_client.py --interactive

# Single tool call
python mcp_generic_client.py --tool hello_world --args '{"name": "User"}'

# Read a resource
python mcp_generic_client.py --resource "config://server/info"
```

## Server Features

### MCP Tools (8 tools)

| Tool | Description |
|------|-------------|
| `hello_world` | Simple greeting tool |
| `calculate` | Math operations (add, subtract, multiply, divide, power, sqrt) |
| `create_task` | Create tasks with Pydantic validation |
| `list_tasks` | List tasks with filtering |
| `analyze_text` | Text analysis with sentiment and keywords |
| `convert_data` | Convert between JSON, CSV, YAML, XML |
| `generate_sample_data` | Generate test data (users, products, events) |
| `increment_counter` | Stateful counter operations |

### MCP Resources (6 resources)

| URI | Description |
|-----|-------------|
| `config://server/info` | Server configuration and status |
| `config://server/stats` | Server statistics |
| `tasks://{task_id}` | Get task by ID |
| `data://samples/{data_type}` | Sample data by type |
| `docs://api/tools` | Tools documentation |
| `docs://api/resources` | Resources documentation |

### MCP Prompts (3 prompts)

| Prompt | Description |
|--------|-------------|
| `task_creation_prompt` | Template for creating well-structured tasks |
| `data_analysis_prompt` | Template for data analysis requests |
| `code_review_prompt` | Multi-turn code review conversation |

## Client Features

The generic client (`mcp_generic_client.py`) provides:

- **No Vendor Lock-in**: Uses standard `httpx` library
- **REST API Communication**: Works with any HTTP-based MCP server
- **Interactive CLI**: Command-line interface for exploration
- **Programmatic API**: Python API for integration

### Client Modes

```bash
# Demo mode - runs through all features
python mcp_generic_client.py --demo

# Interactive mode - REPL-style interface
python mcp_generic_client.py --interactive

# Direct tool execution
python mcp_generic_client.py --tool calculate --args '{"operation": "add", "a": 10, "b": 5}'

# Resource reading
python mcp_generic_client.py --resource "config://server/stats"

# List available tools/resources
python mcp_generic_client.py --list-tools
python mcp_generic_client.py --list-resources
```

### Interactive CLI Commands

When running in interactive mode (`--interactive`):

```
mcp> help              # Show available commands
mcp> health            # Check server health
mcp> tools             # List available tools
mcp> call hello_world {"name": "Developer"}
mcp> resources         # List available resources
mcp> read config://server/info
mcp> prompts           # List available prompts
mcp> exit              # Exit the client
```

## Programmatic Usage

### Python Client Example

```python
import asyncio
from mcp_generic_client import MCPClient

async def main():
    async with MCPClient("http://localhost:8080") as client:
        # Check health
        health = await client.health_check()
        print(f"Server status: {health['status']}")

        # List tools
        tools = await client.list_tools()
        print(f"Available tools: {[t.name for t in tools]}")

        # Call a tool
        result = await client.call_tool("hello_world", {"name": "Python"})
        if result.success:
            print(f"Result: {result.result}")

        # Read a resource
        resource = await client.read_resource("config://server/info")
        print(f"Server info: {resource}")

asyncio.run(main())
```

### cURL Examples

```bash
# Health check
curl http://localhost:8080/api/health

# List tools
curl http://localhost:8080/api/tools

# Call a tool
curl -X POST http://localhost:8080/api/tools/hello_world \
  -H "Content-Type: application/json" \
  -d '{"name": "cURL User"}'

# Call calculate tool
curl -X POST http://localhost:8080/api/tools/calculate \
  -H "Content-Type: application/json" \
  -d '{"operation": "multiply", "a": 7, "b": 6}'

# List resources
curl http://localhost:8080/api/resources

# Read a resource (URL-encoded URI)
curl "http://localhost:8080/api/resources/config%3A%2F%2Fserver%2Finfo"

# List prompts
curl http://localhost:8080/api/prompts
```

## Testing the Setup

### Step 1: Start the Server

```bash
# Terminal 1
python mcp_showcase_server.py
```

You should see:
```
╔══════════════════════════════════════════════════════════════════╗
║                    MCP Showcase Server                            ║
╠══════════════════════════════════════════════════════════════════╣
║  Gradio UI:    http://0.0.0.0:8080/                              ║
║  MCP Endpoint: http://0.0.0.0:8080/mcp                           ║
║  REST API:     http://0.0.0.0:8080/api/                          ║
║  API Docs:     http://0.0.0.0:8080/docs                          ║
╚══════════════════════════════════════════════════════════════════╝
```

### Step 2: Run Client Demo

```bash
# Terminal 2
python mcp_generic_client.py --demo
```

Expected output:
```
============================================================
MCP Generic Client - Demo
Server: http://localhost:8080
============================================================

1. Health Check
----------------------------------------
   Status: healthy
   Server: MCP Showcase Server

2. Available Tools
----------------------------------------
   - hello_world
   - calculate
   - create_task
   ...

3. Call 'hello_world' Tool
----------------------------------------
   Result: Hello, Demo User! Welcome to the MCP Showcase Server.

...
```

### Step 3: Interactive Testing

```bash
python mcp_generic_client.py --interactive
```

Try these commands:
```
mcp> health
mcp> tools
mcp> call hello_world {"name": "Tester"}
mcp> call calculate {"operation": "power", "a": 2, "b": 10}
mcp> resources
mcp> read config://server/stats
mcp> exit
```

### Step 4: Web UI Testing

Open http://localhost:8080 in your browser to access the Gradio interface.

Navigate through the tabs:
1. **Tools**: Test each tool interactively
2. **Resources**: Access server resources
3. **Prompts**: Generate prompt templates
4. **API & MCP Endpoints**: View endpoint documentation

## Configuration

### Server Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `MCP_SERVER_PORT` | 8080 | Server port |
| `MCP_SERVER_HOST` | 0.0.0.0 | Server host |
| `LOG_LEVEL` | INFO | Logging level |

### Client Options

```bash
python mcp_generic_client.py --help

Options:
  --url, -u      Server URL (default: http://localhost:8080)
  --demo, -d     Run demonstration
  --interactive  Start interactive CLI
  --tool, -t     Tool name to execute
  --args, -a     JSON arguments for tool
  --resource, -r Resource URI to read
  --list-tools   List all available tools
  --list-resources List all available resources
```

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    MCP Showcase Server                       │
├─────────────────────────────────────────────────────────────┤
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────────────┐  │
│  │  Gradio UI  │  │  REST API   │  │  MCP Endpoint (SSE) │  │
│  │    (/)      │  │   (/api)    │  │       (/mcp)        │  │
│  └──────┬──────┘  └──────┬──────┘  └──────────┬──────────┘  │
│         │                │                     │             │
│         └────────────────┴─────────────────────┘             │
│                          │                                   │
│              ┌───────────┴───────────┐                       │
│              │     FastMCP Core      │                       │
│              │  ┌─────┐ ┌─────────┐  │                       │
│              │  │Tools│ │Resources│  │                       │
│              │  └─────┘ └─────────┘  │                       │
│              │  ┌───────┐            │                       │
│              │  │Prompts│            │                       │
│              │  └───────┘            │                       │
│              └───────────────────────┘                       │
└─────────────────────────────────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────┐
│                   Generic MCP Client                         │
├─────────────────────────────────────────────────────────────┤
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────────────┐  │
│  │    CLI      │  │ Python API  │  │   Direct HTTP       │  │
│  │ Interface   │  │   (async)   │  │   (cURL, etc.)      │  │
│  └─────────────┘  └─────────────┘  └─────────────────────┘  │
│                          │                                   │
│              ┌───────────┴───────────┐                       │
│              │   httpx (HTTP client) │                       │
│              │   No vendor SDK!      │                       │
│              └───────────────────────┘                       │
└─────────────────────────────────────────────────────────────┘
```

## Key Design Principles

1. **No Vendor Lock-in**: Client uses standard HTTP libraries only
2. **Multiple Interfaces**: Gradio UI, REST API, and MCP protocol
3. **Type Safety**: Pydantic models for input validation
4. **Async-First**: All I/O operations are async
5. **Comprehensive Examples**: Demonstrates various MCP patterns

## Troubleshooting

### Server won't start

```bash
# Check if port is in use
lsof -i :8080

# Use a different port
MCP_SERVER_PORT=9000 python mcp_showcase_server.py
```

### Client can't connect

```bash
# Verify server is running
curl http://localhost:8080/api/health

# Check firewall settings
# Try with explicit URL
python mcp_generic_client.py --url http://127.0.0.1:8080 --demo
```

### Import errors

```bash
# Install all dependencies
pip install fastmcp gradio fastapi uvicorn httpx pydantic aiohttp

# For SSE support (optional)
pip install httpx-sse
```

## License

MIT License - See repository for details.
