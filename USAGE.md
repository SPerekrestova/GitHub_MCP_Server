# GitHub MCP Server - Usage Guide

Complete guide for using the GitHub MCP Server with examples for each tool and resource.

## Table of Contents

- [Setup](#setup)
- [MCP Tools](#mcp-tools)
  - [get_org_repos](#get_org_repos)
  - [get_repo_docs](#get_repo_docs)
  - [get_file_content](#get_file_content)
  - [search_documentation](#search_documentation)
- [MCP Resources](#mcp-resources)
  - [documentation://](#documentation-resource)
  - [content://](#content-resource)
- [Integration Examples](#integration-examples)
- [Common Use Cases](#common-use-cases)
- [Troubleshooting](#troubleshooting)

---

## Setup

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

### Getting Your GitHub Token

1. Go to: https://github.com/settings/tokens
2. Click "Generate new token" → "Generate new token (classic)"
3. Give it a name: "MCP Server Token"
4. Select scopes:
   - `repo` (for private repository access)
   - `read:org` (for organization access)
   - `read:user` (basic user access)
5. Click "Generate token"
6. Copy the token (starts with `ghp_`)
7. Add to `.env` file:
   ```
   GITHUB_TOKEN=ghp_your_actual_token_here
   ```

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

**Command Line Test:**

```bash
python -c "
import asyncio
from main import get_org_repos

async def test():
    repos = await get_org_repos('anthropics')
    print(f'Found {len(repos)} repositories')
    for r in repos[:5]:
        print(f'  - {r[\"name\"]} (has /doc: {r[\"hasDocFolder\"]})')

asyncio.run(test())
"
```

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

**Command Line Test:**

```bash
python -c "
import asyncio
from main import get_repo_docs

async def test():
    docs = await get_repo_docs('anthropics', 'anthropic-sdk-python')
    print(f'Found {len(docs)} documentation files')
    for d in docs:
        print(f'  - {d[\"name\"]} ({d[\"type\"]}, {d[\"size\"]} bytes)')

asyncio.run(test())
"
```

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

**Command Line Test:**

```bash
python -c "
import asyncio
from main import get_file_content

async def test():
    content = await get_file_content(
        'anthropics',
        'anthropic-sdk-python',
        'doc/README.md'
    )
    print(f'File: {content[\"name\"]}')
    print(f'Size: {content[\"size\"]} bytes')
    print(f'Preview: {content[\"content\"][:200]}...')

asyncio.run(test())
"
```

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

**Command Line Test:**

```bash
python -c "
import asyncio
from main import search_documentation

async def test():
    results = await search_documentation('anthropics', 'API')
    print(f'Found {len(results)} results')
    for r in results[:5]:
        print(f'  - {r[\"name\"]} in {r[\"repository\"]}')

asyncio.run(test())
"
```

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

## Integration Examples

### Claude Desktop Integration

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

**Configuration file location:**
- macOS: `~/Library/Application Support/Claude/claude_desktop_config.json`
- Windows: `%APPDATA%\Claude\claude_desktop_config.json`
- Linux: `~/.config/Claude/claude_desktop_config.json`

**Important notes:**
- Replace `/absolute/path/to/GitHub_MCP_Server/main.py` with the actual path on your system
- Replace `ghp_your_token_here` with your GitHub personal access token
- The `autoapprove` field allows Claude to use these tools without prompting for permission each time
- Use `python3` or `python` depending on your system (verify with `which python3` or `which python`)
- Ensure the virtual environment dependencies are installed before use (see Setup section)

**Available tools for autoapproval:**
- `get_org_repos_tool` - Fetch all repositories from an organization
- `get_repo_docs_tool` - Get documentation files from a repository
- `get_file_content_tool` - Fetch content of a specific file
- `search_documentation_tool` - Search for documentation across repositories

Then restart Claude Desktop and ask:
- "What documentation exists in the anthropics organization?"
- "Show me the authentication documentation from anthropic-sdk-python"
- "Search for streaming examples in anthropics repos"
- "Read the content of doc/README.md from the anthropic-sdk-python repository"

### Python Integration

```python
import asyncio
from main import get_org_repos, get_repo_docs, get_file_content

async def main():
    # Find repos with documentation
    repos = await get_org_repos("anthropics")
    repos_with_docs = [r for r in repos if r["hasDocFolder"]]

    # Get documentation from first repo
    if repos_with_docs:
        repo_name = repos_with_docs[0]["name"]
        docs = await get_repo_docs("anthropics", repo_name)

        # Read first doc file
        if docs:
            content = await get_file_content(
                "anthropics",
                repo_name,
                docs[0]["path"]
            )
            print(content["content"])

asyncio.run(main())
```

---

## Common Use Cases

### 1. Documentation Inventory

Create an inventory of all documentation across an organization:

```python
import asyncio
from main import get_org_repos, get_repo_docs

async def inventory():
    org = "anthropics"
    repos = await get_org_repos(org)

    inventory = {}
    for repo in repos:
        if repo["hasDocFolder"]:
            docs = await get_repo_docs(org, repo["name"])
            inventory[repo["name"]] = {
                "url": repo["url"],
                "doc_count": len(docs),
                "docs": docs
            }

    return inventory

result = asyncio.run(inventory())
print(f"Total repos with docs: {len(result)}")
```

### 2. Search and Extract

Search for specific topics and extract content:

```python
import asyncio
from main import search_documentation, get_file_content

async def search_and_extract(org, query):
    # Search for files
    results = await search_documentation(org, query)

    # Extract content from each result
    contents = []
    for result in results:
        content = await get_file_content(
            org,
            result["repository"],
            result["path"]
        )
        contents.append({
            "file": result["name"],
            "repo": result["repository"],
            "content": content["content"]
        })

    return contents

results = asyncio.run(search_and_extract("anthropics", "streaming"))
```

### 3. Documentation Migration

Extract documentation for migration to another system:

```python
import asyncio
import os
from main import get_org_repos, get_repo_docs, get_file_content

async def migrate_docs(org, output_dir):
    repos = await get_org_repos(org)

    for repo in repos:
        if not repo["hasDocFolder"]:
            continue

        # Create repo directory
        repo_dir = os.path.join(output_dir, repo["name"])
        os.makedirs(repo_dir, exist_ok=True)

        # Get all docs
        docs = await get_repo_docs(org, repo["name"])

        # Download each doc
        for doc in docs:
            content = await get_file_content(org, repo["name"], doc["path"])

            # Save to file
            output_path = os.path.join(repo_dir, doc["name"])
            with open(output_path, "w") as f:
                f.write(content["content"])

            print(f"Saved: {output_path}")

asyncio.run(migrate_docs("anthropics", "./docs_backup"))
```

---

## Troubleshooting

### Rate Limiting

**Problem:** "Search API rate limit exceeded"

**Solution:**
- Ensure `GITHUB_TOKEN` is set in `.env`
- Authenticated requests have higher rate limits (5,000 vs 60 per hour)
- Wait for rate limit to reset (check headers: `X-RateLimit-Reset`)

### Authentication Issues

**Problem:** "401 Unauthorized"

**Solution:**
- Check that `GITHUB_TOKEN` is correctly set in `.env`
- Verify token hasn't expired: https://github.com/settings/tokens
- Ensure token has required scopes: `repo`, `read:org`, `read:user`

### Repository Not Found

**Problem:** "404 Not Found" when accessing repository

**Solution:**
- Verify organization and repository names are correct
- Check if repository is private (requires token with `repo` scope)
- Ensure repository exists and you have access

### No Documentation Found

**Problem:** `get_repo_docs` returns empty list

**Solution:**
- Check if `/doc` folder exists in repository
- Verify folder name is exactly `doc` (lowercase)
- Ensure folder contains supported file types (`.md`, `.yml`, `.json`, etc.)

### Content Decoding Errors

**Problem:** "Failed to decode content"

**Solution:**
- This usually happens with binary files
- Ensure you're only requesting text files (markdown, YAML, JSON)
- Check file size - very large files may fail

---

## Performance Tips

1. **Use Search API First**: For finding repos with /doc folders, the search API is much faster than listing all repos
2. **Reuse Sessions**: The implementation reuses aiohttp sessions for better performance
3. **Batch Operations**: When processing multiple repos, use asyncio to run operations concurrently
4. **Cache Results**: Consider caching results to avoid repeated API calls
5. **Rate Limit Awareness**: Monitor rate limit headers and implement backoff strategies for production use

---

## API Reference

For complete API documentation including function signatures, return types, and error handling, see the docstrings in `main.py`.

---

## Support

- **Issues**: Report bugs or request features at the repository's issue tracker
- **Documentation**: See `README.md` for setup and overview
- **Examples**: Check `test_all.py` for working examples

---

## License

MIT
