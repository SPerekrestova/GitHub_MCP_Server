# GitHub MCP Server - Usage Guide

Complete guide for using the GitHub MCP Server with examples for each tool and resource.

## Table of Contents

- [Quick Start with Docker (Recommended)](#quick-start-with-docker-recommended)
- [Getting Your GitHub Token](#getting-your-github-token)
- [MCP Tools](#mcp-tools)
  - [get_org_repos](#get_org_repos)
  - [get_repo_docs](#get_repo_docs)
  - [get_file_content](#get_file_content)
  - [search_documentation](#search_documentation)
- [MCP Resources](#mcp-resources)
  - [documentation://](#documentation-resource)
  - [content://](#content-resource)
- [Docker Deployment](#docker-deployment)
- [Integration Examples](#integration-examples)
- [Common Use Cases](#common-use-cases)
- [Alternative Setup: Python](#alternative-setup-python-for-developers)
- [Troubleshooting](#troubleshooting)

---

## Quick Start with Docker (Recommended)

The easiest way to use the GitHub MCP Server is with Docker - no Python installation required.

### Why Docker?

Docker provides the simplest, most reliable deployment method:

✅ **Zero Python setup** - No version conflicts, no virtual environments
✅ **Cross-platform** - Identical behavior on macOS, Windows, and Linux
✅ **Easy updates** - Single command to get the latest version
✅ **Complete isolation** - No impact on your system packages
✅ **Production-ready** - Secure, tested, optimized builds
✅ **Multi-architecture** - Native support for Intel/AMD and Apple Silicon

### Prerequisites

1. Docker installed ([Get Docker](https://docs.docker.com/get-docker/))
2. GitHub personal access token (see [Getting Your GitHub Token](#getting-your-github-token))

### Step 1: Pull the Image

```bash
docker pull ghcr.io/sperekrestova/github-mcp-server:latest
```

### Step 2: Configure Claude Desktop

**Find your config file:**
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
        "-e", "GITHUB_API_BASE_URL",
        "-e", "LOG_LEVEL",
        "ghcr.io/sperekrestova/github-mcp-server:latest"
      ],
      "env": {
        "GITHUB_TOKEN": "ghp_your_token_here",
        "GITHUB_API_BASE_URL": "https://api.github.com",
        "LOG_LEVEL": "INFO"
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

### Step 3: Restart Claude Desktop

Then ask Claude:
- "What documentation exists in the anthropics organization?"
- "Show me the authentication documentation from anthropic-sdk-python"
- "Search for streaming examples in anthropics repos"

---

## Getting Your GitHub Token

1. Go to: https://github.com/settings/tokens
2. Click "Generate new token" → "Generate new token (classic)"
3. Give it a name: "MCP Server Token"
4. Select scopes:
   - `repo` (for private repository access)
   - `read:org` (for organization access)
   - `read:user` (basic user access)
5. Click "Generate token"
6. Copy the token (starts with `ghp_`)
7. Add to your Claude Desktop configuration

---

## MCP Tools

### get_org_repos

Fetch all repositories from a GitHub organization, detecting which ones have a `/doc` folder.

**Parameters:**
- `org` (string): GitHub organization name

**Returns:**
List of repository objects with:
- `id`: Repository ID
- `name`: Repository name
- `description`: Repository description
- `url`: GitHub URL
- `hasDocFolder`: Boolean indicating if /doc folder exists

**Example Usage:**

```python
# Via MCP client
result = await mcp_client.call_tool("get_org_repos", {
    "org": "anthropics"
})

repos = result.content

# Process results
for repo in repos:
    if repo["hasDocFolder"]:
        print(f"✓ {repo['name']} - {repo['url']}")
```

**Via Claude Desktop:**

Simply ask Claude: *"What repositories with documentation exist in the anthropics organization?"*

**Use Cases:**
- Discover which repositories have documentation
- Inventory all repos in an organization
- Find repos to document

---

### get_repo_docs

Get all documentation files from a repository's `/doc` folder.

**Parameters:**
- `org` (string): GitHub organization name
- `repo` (string): Repository name

**Returns:**
List of documentation file objects with:
- `id`: File SHA
- `name`: Filename
- `path`: Full path in repository
- `type`: Content type (markdown, mermaid, svg, openapi, postman)
- `size`: File size in bytes
- `url`: GitHub URL to file
- `download_url`: Raw content URL
- `sha`: Git SHA hash

**Supported File Types:**
- Markdown (`.md`)
- Mermaid diagrams (`.mmd`, `.mermaid`)
- SVG images (`.svg`)
- OpenAPI specifications (`.yml`, `.yaml`, `.json`)
- Postman collections (`postman*.json`)

**Example Usage:**

```python
# Via MCP client
result = await mcp_client.call_tool("get_repo_docs", {
    "org": "anthropics",
    "repo": "anthropic-sdk-python"
})

docs = result.content

# Group by type
by_type = {}
for doc in docs:
    doc_type = doc["type"]
    by_type[doc_type] = by_type.get(doc_type, 0) + 1

print("Documentation files by type:")
for doc_type, count in by_type.items():
    print(f"  {doc_type}: {count}")
```

**Via Claude Desktop:**

Ask Claude: *"List all documentation files in the anthropic-sdk-python repository"*

**Use Cases:**
- List all documentation in a repository
- Identify documentation types available
- Prepare for content extraction

---

### get_file_content

Fetch the content of a specific file from a GitHub repository.

**Parameters:**
- `org` (string): GitHub organization name
- `repo` (string): Repository name
- `path` (string): File path within repository (e.g., "doc/README.md")

**Returns:**
File object with:
- `name`: Filename
- `path`: Full path
- `content`: Decoded file content as string
- `size`: File size in bytes
- `sha`: Git SHA hash
- `encoding`: Original encoding (usually "base64")

**Example Usage:**

```python
# Via MCP client
result = await mcp_client.call_tool("get_file_content", {
    "org": "anthropics",
    "repo": "anthropic-sdk-python",
    "path": "doc/README.md"
})

file_data = result.content
content = file_data["content"]

# Process markdown content
print(f"File: {file_data['name']}")
print(f"Size: {file_data['size']} bytes")
print(f"\nContent:\n{content}")
```

**Via Claude Desktop:**

Ask Claude: *"Show me the content of doc/README.md from the anthropic-sdk-python repository"*

**Use Cases:**
- Read documentation content
- Extract code examples from docs
- Process markdown for LLM context

---

### search_documentation

Search for documentation files across all repositories in an organization.

**Parameters:**
- `org` (string): GitHub organization name
- `query` (string): Search query

**Returns:**
List of search result objects with:
- `name`: Filename
- `path`: Full path in repository
- `repository`: Repository name
- `url`: GitHub URL to file
- `sha`: Git SHA hash

**Example Usage:**

```python
# Via MCP client
result = await mcp_client.call_tool("search_documentation", {
    "org": "anthropics",
    "query": "authentication"
})

results = result.content

print(f"Found {len(results)} files mentioning 'authentication':")
for r in results:
    print(f"  - {r['repository']}/{r['path']}")
    print(f"    URL: {r['url']}")
```

**Via Claude Desktop:**

Ask Claude: *"Search for authentication examples in anthropics documentation"*

**Use Cases:**
- Find documentation by keyword
- Discover relevant docs across multiple repos
- Build search indexes

**Note:** This tool uses the GitHub Code Search API which has rate limits. If you exceed the limit, you'll receive a rate limit error.

---

## MCP Resources

### documentation:// Resource

Access documentation file listings via URI.

**URI Pattern:**
```
documentation://{organization}/{repository}
```

**Example URIs:**
- `documentation://anthropics/anthropic-sdk-python`
- `documentation://openai/openai-python`
- `documentation://microsoft/vscode`

**Returns:**
Formatted text listing all documentation files with their types and sizes.

**Example Usage:**

```python
# Via MCP client
content = await mcp_client.read_resource(
    "documentation://anthropics/anthropic-sdk-python"
)

print(content)
# Output:
# Documentation in anthropics/anthropic-sdk-python
# ==================================================
#
# 📄 README.md
#    Type: markdown
#    Size: 2,456 bytes
#    Path: doc/README.md
#
# 📄 api.yml
#    Type: openapi
#    Size: 15,234 bytes
#    Path: doc/api.yml
#
# Total: 2 files
```

**Use Cases:**
- Quick overview of available documentation
- Browse documentation structure
- Integration with MCP resource browsers

---

### content:// Resource

Access file content directly via URI.

**URI Pattern:**
```
content://{organization}/{repository}/{path/to/file}
```

**Example URIs:**
- `content://anthropics/anthropic-sdk-python/doc/README.md`
- `content://openai/openai-python/doc/guides/authentication.md`
- `content://microsoft/vscode/doc/api/overview.md`

**Returns:**
Raw file content as string.

**Example Usage:**

```python
# Via MCP client
content = await mcp_client.read_resource(
    "content://anthropics/anthropic-sdk-python/doc/README.md"
)

print(content)
# Output: (raw markdown content)
# # Anthropic SDK Documentation
#
# Welcome to the Anthropic SDK...
```

**Use Cases:**
- Direct file access without tool calls
- Streaming documentation content
- Integration with resource-based workflows

---

## Docker Deployment

### Building Docker Image Locally

If you prefer to build the image yourself:

```bash
# Clone the repository
git clone https://github.com/SPerekrestova/GitHub_MCP_Server.git
cd GitHub_MCP_Server

# Build the image
docker build -t github-mcp-server:local .

# Run your local build
docker run -i --rm \
  -e GITHUB_TOKEN=ghp_your_token_here \
  github-mcp-server:local
```

**Using local build with Claude Desktop:**

Replace `ghcr.io/sperekrestova/github-mcp-server:latest` with `github-mcp-server:local` in your configuration.

### Docker Compose

For easier local development and testing:

```bash
# Create a .env file
echo "GITHUB_TOKEN=ghp_your_token_here" > .env

# Start the service
docker-compose up

# Or run in detached mode
docker-compose up -d

# Stop the service
docker-compose down
```

### Running Docker Manually

```bash
# Run interactively
docker run -i --rm \
  -e GITHUB_TOKEN=ghp_your_token_here \
  ghcr.io/sperekrestova/github-mcp-server:latest

# With additional environment variables
docker run -i --rm \
  -e GITHUB_TOKEN=ghp_your_token_here \
  -e GITHUB_API_BASE_URL=https://api.github.com \
  -e LOG_LEVEL=DEBUG \
  ghcr.io/sperekrestova/github-mcp-server:latest
```

### Docker Image Details

- **Base**: Python 3.10 Alpine Linux
- **Size**: ~50 MB (compressed)
- **User**: Non-root `app` user
- **Architectures**: linux/amd64, linux/arm64 (multi-platform)
- **Security**: Minimal attack surface, no root access
- **Updates**: Automatic builds on every release

---

## Integration Examples

### Example 1: Documentation Inventory

Create an inventory of all documentation across an organization using Claude Desktop with Docker:

**Ask Claude:**
*"Create a complete inventory of all documentation in the anthropics organization. For each repository with docs, list the number and types of documentation files."*

Claude will use the Docker-deployed server to:
1. Get all repos with `get_org_repos_tool`
2. For each repo with docs, use `get_repo_docs_tool`
3. Summarize the findings

### Example 2: Search and Extract

Find specific topics across all documentation:

**Ask Claude:**
*"Search for all documentation about streaming in the anthropics organization and summarize the key points from each file."*

Claude will:
1. Use `search_documentation_tool` to find relevant files
2. Use `get_file_content_tool` to read each file
3. Summarize the content

### Example 3: Migration Planning

**Ask Claude:**
*"I need to migrate documentation from the anthropics organization. Create a migration plan showing which repos have docs, what formats they use, and estimate the total size."*

---

## Common Use Cases

### 1. Finding API Documentation

**Ask Claude:**
*"Find all OpenAPI specification files in the anthropics organization"*

The server will search for `.yml`, `.yaml`, and `.json` files and filter for OpenAPI specs.

### 2. Reviewing README Files

**Ask Claude:**
*"Show me all README.md files from the /doc folders in anthropics repositories"*

### 3. Tracking Documentation Coverage

**Ask Claude:**
*"Which repositories in the anthropics organization don't have documentation folders?"*

### 4. Content Analysis

**Ask Claude:**
*"Analyze the documentation structure of the anthropic-sdk-python repository and suggest improvements"*

---

## Alternative Setup: Python (For Developers)

**Use this method if:**
- You're developing or modifying the server code
- You don't have Docker installed
- You prefer running Python directly
- You need to debug or extend the codebase

### Prerequisites

1. Python 3.10 or higher
2. GitHub personal access token
3. Required Python packages (see `requirements.txt`)

### Installation

```bash
# Clone or download the repository
cd GitHub_MCP_Server

# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env and add your GITHUB_TOKEN
```

### Running Locally

```bash
# Activate virtual environment
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Run the server
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
- Use `python3` or `python` depending on your system (verify with `which python3` or `which python`)
- Ensure the virtual environment dependencies are installed before use

### Testing (Python Development)

```bash
# Run test suite
python test_all.py

# Test specific functionality
python -c "
import asyncio
from main import get_org_repos

async def test():
    repos = await get_org_repos('anthropics')
    print(f'Found {len(repos)} repositories')

asyncio.run(test())
"
```

---

## Troubleshooting

### Docker Issues

#### Permission Denied

**Problem:** "docker: permission denied"

**Solution:**
```bash
# Add your user to the docker group (Linux)
sudo usermod -aG docker $USER
# Log out and back in for changes to take effect

# Or use sudo (not recommended for production)
sudo docker run ...
```

#### Image Pull Fails

**Problem:** "Error pulling image"

**Solution:**
```bash
# Check Docker is running
docker ps

# Try pulling explicitly
docker pull ghcr.io/sperekrestova/github-mcp-server:latest

# Check your internet connection and registry access
```

#### Container Exits Immediately

**Problem:** Container starts then exits

**Solution:**
```bash
# Check logs
docker logs <container-id>

# Ensure GITHUB_TOKEN is set
docker run -i --rm \
  -e GITHUB_TOKEN=ghp_your_token_here \
  ghcr.io/sperekrestova/github-mcp-server:latest

# Verify token is valid at https://github.com/settings/tokens
```

### GitHub API Issues

#### Rate Limiting

**Problem:** "Search API rate limit exceeded"

**Solution:**
- Ensure `GITHUB_TOKEN` is set (authenticated requests have higher limits)
- Authenticated: 5,000 requests/hour
- Unauthenticated: 60 requests/hour
- Wait for rate limit to reset (check headers: `X-RateLimit-Reset`)

#### Authentication Issues

**Problem:** "401 Unauthorized"

**Solution:**
- Check that `GITHUB_TOKEN` is correctly set
- Verify token hasn't expired: https://github.com/settings/tokens
- Ensure token has required scopes: `repo`, `read:org`, `read:user`

#### Repository Not Found

**Problem:** "404 Not Found" when accessing repository

**Solution:**
- Verify organization and repository names are correct
- Check if repository is private (requires token with `repo` scope)
- Ensure repository exists and you have access

### Claude Desktop Issues

#### Server Not Connecting

**Problem:** Claude Desktop can't connect to MCP server

**Solution:**
1. Verify configuration syntax in `claude_desktop_config.json`
2. Check Docker is running: `docker ps`
3. Test the server manually:
   ```bash
   docker run -i --rm -e GITHUB_TOKEN=xxx ghcr.io/sperekrestova/github-mcp-server:latest
   ```
4. Check Claude Desktop logs for error messages
5. Restart Claude Desktop after configuration changes

#### Tools Not Appearing

**Problem:** GitHub MCP tools don't show up in Claude

**Solution:**
1. Ensure configuration is in the correct file location
2. Restart Claude Desktop completely (quit and relaunch)
3. Check for JSON syntax errors in config file
4. Verify the server is listed in Claude's MCP servers list

---

## Performance Tips

1. **Use Docker** - Faster startup and consistent performance
2. **Reuse Sessions** - The implementation reuses aiohttp sessions for better performance
3. **Batch Operations** - When processing multiple repos, operations run concurrently
4. **Cache Results** - Consider caching results to avoid repeated API calls
5. **Rate Limit Awareness** - Monitor rate limit headers and implement backoff strategies for production use

---

## Deployment Comparison

| Feature | Docker (Recommended) | Python (Alternative) |
|---------|---------------------|---------------------|
| Setup complexity | ⭐ Simple | ⭐⭐⭐ Complex |
| Python required | ❌ No | ✅ Yes (3.10+) |
| Dependencies | ✅ Included | ⚠️ Manual install |
| Updates | `docker pull` | `git pull` + `pip install` |
| Isolation | ✅ Complete | ⚠️ Virtual env only |
| Cross-platform | ✅ Identical | ⚠️ May vary |
| For end users | ✅ Recommended | ❌ Not recommended |
| For developers | ✅ Supported | ✅ Recommended |
| Debugging | ⚠️ More complex | ✅ Easy |
| Customization | ⚠️ Requires rebuild | ✅ Immediate |

---

## Support

- **Issues**: Report bugs or request features at the repository's issue tracker
- **Documentation**: See `README.md` for setup and overview
- **Examples**: Check `test_all.py` for working examples
- **Docker Hub**: Pre-built images at `ghcr.io/sperekrestova/github-mcp-server`

---

## License

MIT
