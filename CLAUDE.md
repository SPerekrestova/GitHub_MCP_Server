# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

GitHub MCP Server - A Model Context Protocol (MCP) server that provides GitHub API access for fetching and searching documentation in `/doc` folders across GitHub organizations. Built with FastMCP.

## Development Commands

```bash
# Setup
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env  # Add GITHUB_TOKEN

# Run locally (stdio transport for Claude Desktop)
python main.py

# Run with HTTP transport (for Hugging Face Spaces)
# Set MCP_HTTP_TRANSPORT=true or modify main.py to use mcp.run(transport="http")
```

## Architecture

**Single-file MCP server** (`main.py`) using FastMCP framework:

1. **MCP Tools** (decorated with `@mcp.tool()`):
   - `get_org_repos_tool` - List repos with `/doc` folder detection (uses Search API first, falls back to listing all)
   - `get_repo_docs_tool` - Get documentation files from repo's `/doc` folder
   - `get_file_content_tool` - Fetch and decode file content (handles base64)
   - `search_documentation_tool` - Search docs across org using GitHub Code Search API

2. **MCP Resources** (decorated with `@mcp.resource()`):
   - `documentation://{org}/{repo}` - List docs
   - `content://{org}/{repo}/{path}` - Get file content

3. **Business Logic Functions** (async, testable):
   - `get_org_repos()`, `get_repo_docs()`, `get_file_content()`, `search_documentation()`
   - Each tool is a thin wrapper calling these functions

## Key Implementation Details

- **GitHub API strategy**: Search API first for efficiency, fallback to paginated list + check each repo
- **Supported doc types**: `.md`, `.mmd`, `.mermaid`, `.svg`, `.yml`, `.yaml`, `.json`
- **Content decoding**: Base64 content from GitHub API is automatically decoded
- **Health check**: `/health` endpoint available via `@mcp.custom_route()`

## Environment Variables

- `GITHUB_TOKEN` - Required for API access (scopes: `repo`, `read:org`, `read:user`)
- `GITHUB_API_BASE_URL` - Default: `https://api.github.com`
- `LOG_LEVEL` - Default: `INFO`

## CI/CD

Docker image published to `ghcr.io/sperekrestova/github-mcp-server` on push to main or version tags. Multi-platform build (amd64/arm64).