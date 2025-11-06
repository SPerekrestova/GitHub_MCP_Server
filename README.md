# GitHub MCP Server

Model Context Protocol server for GitHub API integration.

## Features

- Fetch repositories from GitHub organizations with /doc folder detection
- Access documentation files from repositories
- Search across documentation in an organization
- Get file content with automatic base64 decoding
- MCP-compliant tools and resources
- Async/await design for performance

## Setup

1. Create virtual environment:
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Configure environment:
   ```bash
   cp .env.example .env
   # Edit .env and add your GITHUB_TOKEN
   ```

   Get your GitHub token from: https://github.com/settings/tokens
   Required scopes: `repo`, `read:org`, `read:user`

4. Run server:
   ```bash
   python main.py
   ```

## Environment Variables

- `GITHUB_TOKEN` - GitHub personal access token (required for higher rate limits)
- `GITHUB_API_BASE_URL` - GitHub API URL (default: https://api.github.com)
- `MCP_SERVER_PORT` - Server port (default: 8000)
- `LOG_LEVEL` - Logging level (default: INFO)

## MCP Tools

### get_org_repos(org: str)
Fetch all repositories from an organization, detecting which have /doc folders.

**Usage:**
```python
repos = await mcp_client.call_tool("get_org_repos", {"org": "anthropics"})
```

### get_repo_docs(org: str, repo: str)
Get all documentation files from a repository's /doc folder.

**Usage:**
```python
docs = await mcp_client.call_tool("get_repo_docs", {
    "org": "anthropics",
    "repo": "anthropic-sdk-python"
})
```

### get_file_content(org: str, repo: str, path: str)
Fetch content of a specific file with automatic base64 decoding.

**Usage:**
```python
content = await mcp_client.call_tool("get_file_content", {
    "org": "anthropics",
    "repo": "anthropic-sdk-python",
    "path": "doc/README.md"
})
```

### search_documentation(org: str, query: str)
Search for documentation files across all repositories in an organization.

**Usage:**
```python
results = await mcp_client.call_tool("search_documentation", {
    "org": "anthropics",
    "query": "streaming"
})
```

## MCP Resources

### documentation://{org}/{repo}
List documentation files in a repository.

**Example URI:**
```
documentation://anthropics/anthropic-sdk-python
```

### content://{org}/{repo}/{path}
Get file content directly via URI.

**Example URI:**
```
content://anthropics/anthropic-sdk-python/doc/README.md
```

## Claude Desktop Integration

Add to your `claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "github-docs": {
      "command": "python",
      "args": ["/path/to/GitHub_MCP_Server/main.py"],
      "env": {
        "GITHUB_TOKEN": "ghp_your_token_here"
      }
    }
  }
}
```

Then restart Claude Desktop and ask:
- "What documentation exists in the anthropics organization?"
- "Show me authentication docs from the SDK"
- "Search for streaming examples in anthropics repos"

## Testing

Run the comprehensive test suite:
```bash
python test_all.py
```

## Supported Documentation Formats

- Markdown (`.md`)
- Mermaid diagrams (`.mmd`, `.mermaid`)
- SVG images (`.svg`)
- OpenAPI specifications (`.yml`, `.yaml`, `.json`)
- Postman collections (`.json`)

## License

MIT
