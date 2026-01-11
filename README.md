---
title: GitHub MCP Server
emoji: 🐙
colorFrom: blue
colorTo: purple
sdk: docker
app_port: 7860
---

# GitHub MCP Server

Model Context Protocol server for accessing GitHub documentation via API.

## Features

- Fetch repositories from organizations with `/doc` folder detection
- Access documentation files from repositories
- Search across documentation
- Automatic base64 decoding
- MCP-compliant tools and resources

## Quick Start (Docker)

### 1. Pull the image

```bash
docker pull ghcr.io/sperekrestova/github-mcp-server:latest
```

### 2. Configure Claude Desktop

Add to `claude_desktop_config.json`:

**macOS**: `~/Library/Application Support/Claude/claude_desktop_config.json`
**Windows**: `%APPDATA%\Claude\claude_desktop_config.json`
**Linux**: `~/.config/Claude/claude_desktop_config.json`

```json
{
  "mcpServers": {
    "github-docs": {
      "command": "docker",
      "args": [
        "run",
        "-i",
        "--rm",
        "-e", "GITHUB_TOKEN",
        "ghcr.io/sperekrestova/github-mcp-server:latest"
      ],
      "env": {
        "GITHUB_TOKEN": "ghp_your_token_here"
      },
      "autoapprove": [
        "get_org_repos_tool",
        "get_repo_docs_tool",
        "get_file_content_tool",
        "search_documentation_tool"
      ]
    }
  }
}
```

### 3. Get GitHub Token

1. Go to https://github.com/settings/tokens
2. Generate new token (classic)
3. Required scopes: `repo`, `read:org`, `read:user`
4. Add token to configuration above

### 4. Restart Claude Desktop

Ask Claude:
- "What documentation exists in the anthropics organization?"
- "Show me docs from the anthropic-sdk-python repository"
- "Search for streaming examples in anthropics repos"

## MCP Tools

- **get_org_repos(org)** - List repositories with /doc folder detection
- **get_repo_docs(org, repo)** - Get documentation files from repository
- **get_file_content(org, repo, path)** - Fetch file content with base64 decoding
- **search_documentation(org, query)** - Search documentation across repositories

## MCP Resources

- `documentation://{org}/{repo}` - List documentation files
- `content://{org}/{repo}/{path}` - Get file content

## Building from Source

**Local Docker build:**
```bash
# Enable BuildKit for faster builds
export DOCKER_BUILDKIT=1

# Build (~30 seconds with cache)
docker build -t github-mcp-server:local .

# Or use docker-compose
docker-compose build
```

**Python setup (for development):**
```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
# Add GITHUB_TOKEN to .env
python main.py
```

**Claude Desktop config (Python):**
```json
{
  "mcpServers": {
    "github-docs": {
      "command": "python3",
      "args": ["/absolute/path/to/main.py"],
      "env": {
        "GITHUB_TOKEN": "ghp_your_token_here"
      },
      "autoapprove": ["get_org_repos_tool", "get_repo_docs_tool", "get_file_content_tool", "search_documentation_tool"]
    }
  }
}
```

## Environment Variables

- `GITHUB_TOKEN` - GitHub personal access token (required)
- `GITHUB_API_BASE_URL` - GitHub API URL (default: https://api.github.com)
- `LOG_LEVEL` - Logging level (default: INFO)

## Supported File Types

Markdown (`.md`), Mermaid (`.mmd`, `.mermaid`), SVG (`.svg`), OpenAPI (`.yml`, `.yaml`, `.json`), Postman collections (`.json`)

## License

MIT
