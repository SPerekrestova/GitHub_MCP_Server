# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Overview

GitHub MCP Server is a Model Context Protocol (MCP) server that provides access to GitHub documentation via the GitHub API. It's built with FastMCP and runs as a stdio-based MCP server, designed to be integrated with Claude Desktop or other MCP clients.

## Development Commands

### Environment Setup

```bash
# Create and activate virtual environment
python3 -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env and add your GITHUB_TOKEN
```

### Running the Server

```bash
# Run directly with Python (stdio mode for MCP)
python main.py

# Run with Docker
docker build -t github-mcp-server:local .
docker run -i --rm -e GITHUB_TOKEN='your_token' github-mcp-server:local

# Run with docker-compose
docker-compose build
docker-compose up
```

### Docker Build Performance

The Dockerfile is optimized for fast rebuilds (10-20x faster):
- Uses BuildKit for layer caching
- Separates dependency installation from code copying
- Enable BuildKit: `export DOCKER_BUILDKIT=1`

## Architecture

### Single-File Architecture

The entire server is implemented in `main.py` (~650 lines) with a clear functional organization:

1. **Configuration & Setup** (lines 1-37): Environment loading, logging, MCP initialization
2. **Helper Functions** (lines 39-114): GitHub API headers, /doc folder detection, content type determination
3. **Business Logic Functions** (lines 116-442): Core async functions that implement GitHub API interactions
4. **MCP Tools Registration** (lines 444-569): Decorated wrappers that expose business logic as MCP tools
5. **MCP Resources** (lines 571-638): URI-based resource handlers for documentation access
6. **Main Entry Point** (lines 640-652): Server startup

### Key Design Patterns

**Separation of Concerns**: Business logic functions (e.g., `get_org_repos()`) are separate from MCP tool decorators (e.g., `get_org_repos_tool()`). This allows the core logic to be testable independently of MCP.

**Async/Await Throughout**: All GitHub API interactions use `aiohttp` for async HTTP requests. Functions reuse `ClientSession` objects for connection pooling.

**Two-Strategy Approach**: `get_org_repos()` tries GitHub Search API first (efficient, one request), then falls back to listing all repos individually if search fails.

**Base64 Decoding**: GitHub API returns file content as base64-encoded strings. The `get_file_content()` function automatically decodes this to UTF-8 text.

## MCP Integration

### Tools (4 total)

- `get_org_repos_tool(org)` - Lists repositories with /doc folder detection
- `get_repo_docs_tool(org, repo)` - Lists documentation files in a repo's /doc folder
- `get_file_content_tool(org, repo, path)` - Fetches and decodes file content
- `search_documentation_tool(org, query)` - Searches docs across repos using GitHub Code Search API

### Resources (2 patterns)

- `documentation://{org}/{repo}` - Lists documentation files in formatted text
- `content://{org}/{repo}/{path}` - Returns raw file content

### Environment Variables

Required:
- `GITHUB_TOKEN` - GitHub personal access token (scopes: `repo`, `read:org`, `read:user`)

Optional:
- `GITHUB_API_BASE_URL` - Default: `https://api.github.com`
- `LOG_LEVEL` - Default: `INFO`
- `SERVER_PORT` - Default: `8000` (note: not used in stdio mode)

## Supported File Types

The server filters for specific documentation file types in /doc folders:
- Markdown: `.md`
- Mermaid diagrams: `.mmd`, `.mermaid`
- SVG images: `.svg`
- OpenAPI specs: `.yml`, `.yaml`, `.json`
- Postman collections: `.json` (filename must start with "postman")

## Error Handling

- 404 responses return empty lists or specific error messages
- Rate limiting (403 from Search API) returns user-facing error message
- All GitHub API errors include status code and response text
- Missing GITHUB_TOKEN triggers warning but allows unauthenticated requests (with rate limits)

## Claude Desktop Configuration

Add to `claude_desktop_config.json`:

**Docker deployment:**
```json
{
  "mcpServers": {
    "github-docs": {
      "command": "docker",
      "args": ["run", "-i", "--rm", "-e", "GITHUB_TOKEN", "ghcr.io/sperekrestova/github-mcp-server:latest"],
      "env": {"GITHUB_TOKEN": "ghp_your_token_here"}
    }
  }
}
```

**Python deployment:**
```json
{
  "mcpServers": {
    "github-docs": {
      "command": "python3",
      "args": ["/absolute/path/to/main.py"],
      "env": {"GITHUB_TOKEN": "ghp_your_token_here"}
    }
  }
}
```

## Testing Approach

Currently no test suite exists. When adding tests:
- Test business logic functions separately from MCP tool wrappers
- Mock `aiohttp.ClientSession` for GitHub API interactions
- Test base64 decoding edge cases in `get_file_content()`
- Test /doc folder detection logic
- Test file type filtering against supported extensions
