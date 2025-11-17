# GitHub MCP Server

Model Context Protocol server for GitHub API integration.

## Features

- Fetch repositories from GitHub organizations with /doc folder detection
- Access documentation files from repositories
- Search across documentation in an organization
- Get file content with automatic base64 decoding
- MCP-compliant tools and resources
- Async/await design for performance

## Quick Start with Docker (Recommended)

The easiest way to use GitHub MCP Server is with Docker - no Python installation required.

### 1. Pull the Pre-built Image

```bash
docker pull ghcr.io/sperekrestova/github-mcp-server:latest
```

### 2. Configure Claude Desktop

Add this to your `claude_desktop_config.json`:

**Configuration file location:**
- macOS: `~/Library/Application Support/Claude/claude_desktop_config.json`
- Windows: `%APPDATA%\Claude\claude_desktop_config.json`
- Linux: `~/.config/Claude/claude_desktop_config.json`

**Basic configuration:**
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
      }
    }
  }
}
```

**Recommended configuration (with auto-approve):**
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

### 3. Get Your GitHub Token

1. Go to: https://github.com/settings/tokens
2. Generate new token (classic)
3. Required scopes: `repo`, `read:org`, `read:user`
4. Copy token and add to configuration

### 4. Restart Claude Desktop

Then ask Claude:
- "What documentation exists in the anthropics organization?"
- "Show me authentication docs from the SDK"
- "Search for streaming examples in anthropics repos"

### Why Docker?

✅ **No Python installation required** - Works immediately on any system with Docker
✅ **Consistent environment** - Same behavior across macOS, Windows, Linux
✅ **Easy updates** - Just `docker pull` for the latest version
✅ **Isolated dependencies** - No conflicts with your system packages
✅ **Secure** - Runs as non-root user in minimal Alpine container
✅ **Multi-platform** - Supports both Intel/AMD (amd64) and ARM (arm64)

## Environment Variables

- `GITHUB_TOKEN` - GitHub personal access token (required for higher rate limits)
- `GITHUB_API_BASE_URL` - GitHub API URL (default: https://api.github.com)
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

## Advanced Docker Usage

### Building Docker Image Locally

```bash
# Clone the repository
git clone https://github.com/SPerekrestova/GitHub_MCP_Server.git
cd GitHub_MCP_Server

# Build the image
docker build -t github-mcp-server:local .

# Use your local build in Claude Desktop
# Replace "ghcr.io/sperekrestova/github-mcp-server:latest"
# with "github-mcp-server:local" in your config
```

### Using Docker Compose

```bash
# Create .env file
echo "GITHUB_TOKEN=ghp_your_token_here" > .env

# Start the service
docker-compose up

# Or run in detached mode
docker-compose up -d
```

### Running Docker Manually

```bash
# Run interactively
docker run -i --rm \
  -e GITHUB_TOKEN=ghp_your_token_here \
  ghcr.io/sperekrestova/github-mcp-server:latest
```

## Alternative Setup: Python (For Developers)

**Use this method if:**
- You're developing or modifying the server code
- You don't have Docker installed
- You prefer running Python directly

### 1. Create virtual environment

```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### 3. Configure environment

```bash
cp .env.example .env
# Edit .env and add your GITHUB_TOKEN
```

Get your GitHub token from: https://github.com/settings/tokens
Required scopes: `repo`, `read:org`, `read:user`

### 4. Run server

```bash
python main.py
```

### Claude Desktop Configuration (Python)

Add to your `claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "github-docs": {
      "command": "python3",
      "args": ["/absolute/path/to/GitHub_MCP_Server/main.py"],
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

**Important notes:**
- Replace `/absolute/path/to/GitHub_MCP_Server/main.py` with the actual path on your system
- Use `python3` or `python` depending on your system (check with `which python3`)
- Ensure the virtual environment dependencies are installed before use

## Deployment Comparison

| Feature | Docker (Recommended) | Python (Alternative) |
|---------|---------------------|---------------------|
| Setup complexity | ⭐ Simple | ⭐⭐⭐ Complex |
| Python required | ❌ No | ✅ Yes (3.10+) |
| Updates | `docker pull` | `git pull` + `pip install` |
| Isolation | ✅ Complete | ⚠️ Virtual env only |
| Cross-platform | ✅ Identical | ⚠️ May vary |
| For end users | ✅ Recommended | ❌ Not recommended |
| For developers | ✅ Supported | ✅ Recommended |

## Supported Documentation Formats

- Markdown (`.md`)
- Mermaid diagrams (`.mmd`, `.mermaid`)
- SVG images (`.svg`)
- OpenAPI specifications (`.yml`, `.yaml`, `.json`)
- Postman collections (`.json`)

## Testing

Run the comprehensive test suite:
```bash
python test_all.py
```

## License

MIT
