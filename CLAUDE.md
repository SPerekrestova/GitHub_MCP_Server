# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

GitHub MCP Server - A Model Context Protocol (MCP) server that provides GitHub API access for fetching and searching documentation in `/doc` folders across GitHub organizations. Built with Gradio for Hugging Face Spaces deployment.

## Development Commands

```bash
# Setup
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env  # Add GITHUB_TOKEN

# Run locally (starts Gradio server with MCP support)
python main.py
# Server runs on http://localhost:7860
# MCP endpoint: http://localhost:7860/gradio_api/mcp/
```

## Architecture

**Single-file MCP server** (`main.py`) using Gradio with MCP support:

1. **MCP Tools** (exposed via `gr.Interface` with `mcp_server=True`):
   - `get_org_repos_tool` - List repos with `/doc` folder detection (uses Search API first, falls back to listing all)
   - `get_repo_docs_tool` - Get documentation files from repo's `/doc` folder
   - `get_file_content_tool` - Fetch and decode file content (handles base64)
   - `search_documentation_tool` - Search docs across org using GitHub Code Search API

2. **Business Logic Functions** (async, testable):
   - `get_org_repos()`, `get_repo_docs()`, `get_file_content()`, `search_documentation()`
   - Tool functions are async wrappers with error handling

3. **Gradio Interface**:
   - `gr.TabbedInterface` combining 4 tool interfaces
   - Each tool has its own `gr.Interface` for web UI access
   - MCP tools auto-exposed at `/gradio_api/mcp/`

## Key Implementation Details

- **GitHub API strategy**: Search API first for efficiency, fallback to paginated list + check each repo
- **Supported doc types**: `.md`, `.mmd`, `.mermaid`, `.svg`, `.yml`, `.yaml`, `.json`
- **Content decoding**: Base64 content from GitHub API is automatically decoded
- **Error handling**: All tools return JSON with `{"error": "..."}` on failure
- **MCP Schema**: Available at `/gradio_api/mcp/schema`

## Environment Variables

- `GITHUB_TOKEN` - Required for API access (scopes: `repo`, `read:org`, `read:user`)
- `GITHUB_API_BASE_URL` - Default: `https://api.github.com`
- `LOG_LEVEL` - Default: `INFO`

## Hugging Face Spaces Deployment

Configure MCP client with:
```json
{
  "mcpServers": {
    "github-docs": {
      "url": "https://your-space.hf.space/gradio_api/mcp/"
    }
  }
}
```

## CI/CD

Docker image published to `ghcr.io/sperekrestova/github-mcp-server` on push to main or version tags. Multi-platform build (amd64/arm64).